"""
matcher.py — Evidence collection and classification for SkillGraph.

For each skill extracted from a job description, this module searches the
provided AnalysisResult for corroborating code evidence, then assigns one
of three evidence tiers:

  STRONG — Two or more independent evidence signals found, OR an import
           with at least one corroborating symbol/docstring mention.
  WEAK   — Exactly one evidence signal (import alone, or symbol name
           mention alone, or docstring mention alone).
  NONE   — No evidence found in the analyzed repository.

Important constraints:
- An import alone NEVER produces STRONG evidence.
  Rationale: importing a package shows it was used, but does not demonstrate
  understanding of its API or authoring of meaningful code with it.
- Evidence items always carry real file paths, symbol IDs, and line numbers
  from the AnalysisResult. No locations are invented.
- The analysis_result is treated as untrusted client data; only fields
  explicitly listed in the Pydantic schema are accessed.
- No repository code is executed. Evidence is purely textual/structural.
"""

import re
from typing import Dict, List, Optional, Set

from app.services.repomind.models import AnalysisResult, CodeSymbol
from app.services.skillgraph.extractor import ExtractedSkill
from app.services.skillgraph.models import (
    EvidenceItem,
    EvidenceTier,
    MatchSummary,
    SkillMatchResponse,
    SkillResult,
)
from app.services.skillgraph.skill_taxonomy import (
    SKILL_ALIASES,
    SKILL_METADATA,
    aliases_for,
    get_skill_info,
)

_DISCLAIMER = (
    "SkillGraph performs static code analysis only. "
    "Results reflect code artifacts found in the submitted repository analysis, "
    "not personal skill level, proficiency depth, or hiring suitability. "
    "Import presence alone does not prove proficiency."
)

_COVERAGE_NOTE = (
    "This analysis reflects only static code evidence from the submitted repository. "
    "Import presence indicates that a package was referenced in source files, "
    "not that the developer is proficient with it."
)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def match_skills(
    extracted_skills: List[ExtractedSkill],
    analysis_result: Optional[AnalysisResult],
) -> SkillMatchResponse:
    """
    Match a list of extracted skills against an optional AnalysisResult.

    Returns a SkillMatchResponse with per-skill evidence items, tiers,
    explanations, and recommendations.
    """
    # Build lookup structures from the analysis result (if provided)
    import_set: Set[str] = set()
    symbol_list: List[CodeSymbol] = []

    if analysis_result is not None:
        # imported_packages may not be present on older clients — default to []
        for pkg in getattr(analysis_result, "imported_packages", []):
            if isinstance(pkg, str) and pkg.strip():
                import_set.add(pkg.strip().lower())
        symbol_list = list(analysis_result.symbols or [])

    required_results: List[SkillResult] = []
    preferred_results: List[SkillResult] = []

    for skill in extracted_skills:
        result = _evaluate_skill(skill, import_set, symbol_list)
        if skill.is_required:
            required_results.append(result)
        else:
            preferred_results.append(result)

    # Build summary counts
    all_results = required_results + preferred_results
    strong_count = sum(1 for r in all_results if r.evidence_tier == EvidenceTier.STRONG)
    weak_count = sum(1 for r in all_results if r.evidence_tier == EvidenceTier.WEAK)
    none_count = sum(1 for r in all_results if r.evidence_tier == EvidenceTier.NONE)

    summary = MatchSummary(
        required_count=len(required_results),
        preferred_count=len(preferred_results),
        strong_evidence_count=strong_count,
        weak_evidence_count=weak_count,
        no_evidence_count=none_count,
        coverage_note=_COVERAGE_NOTE if analysis_result is not None else (
            "No repository analysis was provided. "
            "All skills are classified as 'no evidence'. "
            "Scan a repository with RepoMind and re-submit to see code evidence."
        ),
    )

    return SkillMatchResponse(
        skills_required=required_results,
        skills_preferred=preferred_results,
        summary=summary,
        disclaimer=_DISCLAIMER,
    )


# ---------------------------------------------------------------------------
# Per-skill evaluation
# ---------------------------------------------------------------------------

def _evaluate_skill(
    skill: ExtractedSkill,
    import_set: Set[str],
    symbols: List[CodeSymbol],
) -> SkillResult:
    """Evaluate a single canonical skill and produce a SkillResult."""
    canonical = skill.canonical_name
    all_aliases = aliases_for(canonical)  # all known aliases for this canonical
    info = get_skill_info(canonical)

    evidence_items: List[EvidenceItem] = []

    # ── Signal 1: Import evidence ──────────────────────────────────────────
    import_evidence = _collect_import_evidence(canonical, all_aliases, import_set)
    evidence_items.extend(import_evidence)

    # ── Signal 2 & 3: Symbol name + docstring evidence ────────────────────
    symbol_evidence = _collect_symbol_evidence(canonical, all_aliases, symbols)
    evidence_items.extend(symbol_evidence)

    # ── Tier classification ────────────────────────────────────────────────
    tier, explanation = _classify_tier(canonical, evidence_items)

    # ── Recommendation ────────────────────────────────────────────────────
    recommendation: Optional[str] = None
    if tier in (EvidenceTier.WEAK, EvidenceTier.NONE) and info:
        recommendation = info.recommendation

    return SkillResult(
        canonical_name=canonical,
        aliases_matched=skill.raw_aliases_found or list({
            a for a in all_aliases if a in (skill.canonical_name, *skill.raw_aliases_found)
        }),
        evidence_tier=tier,
        evidence_items=evidence_items,
        explanation=explanation,
        recommendation=recommendation,
    )


# ---------------------------------------------------------------------------
# Signal collectors
# ---------------------------------------------------------------------------

def _collect_import_evidence(
    canonical: str,
    all_aliases: List[str],
    import_set: Set[str],
) -> List[EvidenceItem]:
    """
    Check whether any alias for this skill appears in the imported_packages list.
    Returns at most one EvidenceItem of kind='import'.
    """
    matched_pkg: Optional[str] = None
    for alias in all_aliases:
        if alias.lower() in import_set:
            matched_pkg = alias
            break

    if matched_pkg is None:
        return []

    return [
        EvidenceItem(
            kind="import",
            package=matched_pkg,
            detail=(
                f"Package '{matched_pkg}' was imported in the repository "
                f"(canonical skill: {canonical}). "
                "Import presence alone is weak evidence; see symbol evidence below."
            ),
        )
    ]


def _collect_symbol_evidence(
    canonical: str,
    all_aliases: List[str],
    symbols: List[CodeSymbol],
) -> List[EvidenceItem]:
    """
    Search symbol names and docstrings for keyword references to this skill.

    Rules:
    - Symbol name matching splits on underscores AND non-word characters so that
      underscore-delimited Python identifiers like 'train_sklearn_model' are
      correctly tokenised (each token is matched as a whole word).
    - Docstring matching uses standard whole-word regex (spaces/punctuation bound).
    - Each match produces one EvidenceItem with the real file_path and line range.
    - A single symbol can generate at most one EvidenceItem (name OR docstring,
      name takes priority to avoid double-counting).
    - Minimum alias length of 3 characters prevents spurious single-letter matches.
    """
    info = get_skill_info(canonical)
    jd_keywords = info.jd_keywords if info else []

    # Keywords to match against symbol names (tokenised by _ and non-word chars).
    # Use aliases only — not generic JD phrases — to keep false-positive rate low.
    name_keywords: Set[str] = {canonical.lower()} | {
        a.lower() for a in all_aliases if len(a) >= 3
    }

    # Keywords for docstring matching (also include descriptive JD phrases).
    doc_keywords: Set[str] = name_keywords | {kw.lower() for kw in jd_keywords}

    # Compile whole-word regex for docstrings (standard word boundaries work in text)
    doc_patterns = [
        re.compile(rf"(?i)\b{re.escape(kw)}\b") for kw in doc_keywords if kw
    ]

    evidence: List[EvidenceItem] = []
    seen_symbol_ids: Set[str] = set()

    _TOKEN_SPLIT = re.compile(r"[_\W]+")

    for sym in symbols:
        if sym.id in seen_symbol_ids:
            continue
        # Skip module symbols (filenames, not authored code)
        if sym.symbol_type == "module":
            continue

        # Tokenise the symbol name on underscores and non-word characters,
        # then check if any lowercase token matches a skill keyword.
        name_tokens = {t.lower() for t in _TOKEN_SPLIT.split(sym.name) if t}
        matched_kw = name_keywords & name_tokens  # set intersection

        if matched_kw:
            kw_str = next(iter(matched_kw))
            evidence.append(EvidenceItem(
                kind="symbol",
                symbol_id=sym.id,
                symbol_name=sym.name,
                file_path=sym.location.file_path,
                start_line=sym.location.start_line,
                end_line=sym.location.end_line,
                detail=(
                    f"Symbol name '{sym.name}' ({sym.symbol_type}) "
                    f"contains token '{kw_str}' referencing '{canonical}'."
                ),
            ))
            seen_symbol_ids.add(sym.id)
            continue  # name match takes priority; skip docstring check for same symbol

        # Check docstring with standard word-boundary patterns
        if sym.docstring:
            doc_matched: Optional[str] = None
            for pat in doc_patterns:
                if pat.search(sym.docstring):
                    doc_matched = pat.pattern
                    break
            if doc_matched:
                evidence.append(EvidenceItem(
                    kind="docstring",
                    symbol_id=sym.id,
                    symbol_name=sym.name,
                    file_path=sym.location.file_path,
                    start_line=sym.location.start_line,
                    end_line=sym.location.end_line,
                    detail=(
                        f"Docstring of '{sym.name}' ({sym.symbol_type}) "
                        f"references '{canonical}'."
                    ),
                ))
                seen_symbol_ids.add(sym.id)

    return evidence


# ---------------------------------------------------------------------------
# Tier classification
# ---------------------------------------------------------------------------

def _classify_tier(
    canonical: str,
    evidence_items: List[EvidenceItem],
) -> tuple:
    """
    Assign a tier and produce a transparent explanation string.

    Classification rules (import alone is never STRONG):
    - STRONG: import evidence present AND at least one symbol/docstring item.
    - STRONG: two or more symbol/docstring items (no import needed).
    - WEAK:   import evidence present but no symbol/docstring corroboration.
    - WEAK:   exactly one symbol/docstring item, no import.
    - NONE:   no evidence items at all.
    """
    import_items = [e for e in evidence_items if e.kind == "import"]
    code_items = [e for e in evidence_items if e.kind in ("symbol", "docstring")]

    has_import = len(import_items) > 0
    code_count = len(code_items)

    if has_import and code_count >= 1:
        explanation = (
            f"Strong evidence: '{canonical}' was imported in the repository "
            f"and corroborated by {code_count} symbol/docstring reference(s). "
            "Import presence combined with authored code usage is a meaningful signal."
        )
        return EvidenceTier.STRONG, explanation

    if code_count >= 2:
        explanation = (
            f"Strong evidence: {code_count} symbol or docstring references to '{canonical}' "
            "were found across the repository without requiring an import match."
        )
        return EvidenceTier.STRONG, explanation

    if has_import and code_count == 0:
        explanation = (
            f"Weak evidence: '{canonical}' was imported in the repository, "
            "but no corroborating symbol names or docstring references were found. "
            "An import alone does not demonstrate active use or authorship."
        )
        return EvidenceTier.WEAK, explanation

    if code_count == 1:
        item = code_items[0]
        explanation = (
            f"Weak evidence: one {item.kind} reference to '{canonical}' was found "
            f"(symbol '{item.symbol_name}' in {item.file_path}), "
            "but no corresponding import or additional corroboration was detected."
        )
        return EvidenceTier.WEAK, explanation

    explanation = (
        f"No evidence: no import, symbol name, or docstring reference to '{canonical}' "
        "was found in the analyzed repository."
    )
    return EvidenceTier.NONE, explanation

