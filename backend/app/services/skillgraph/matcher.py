"""
matcher.py — Evidence collection, confidence rating, and roadmap synthesis for SkillGraph.

Evidence classification rules (enforcing strict safeguards):
- STRONG: Authored code evidence corroborated by an import, OR two or more
  independent authored code signals (API call invocations, symbol definitions, docstrings).
- WEAK:   Single signal only (import alone, or single API call pattern alone,
  or single isolated symbol name/docstring).
- NONE:   No evidence found in the repository.

Critical safeguards:
- An import alone is strictly WEAK evidence (LOW confidence).
- An API call invocation alone is strictly WEAK evidence (HIGH confidence of pattern,
  but single-signal until corroborated by authored code context).
- Every evidence item points to real RepoMind artifacts (real file_path, symbol_id, line numbers).
- Zero source locations are fabricated.
"""

import re
from typing import Dict, List, Optional, Set, Tuple

from app.services.repomind.models import AnalysisResult, CodeSymbol, UnresolvedCall
from app.services.skillgraph.extractor import ExtractedSkill
from app.services.skillgraph.models import (
    EvidenceConfidence,
    EvidenceItem,
    EvidenceTier,
    LearningResourceModel,
    MatchSummary,
    RoadmapTask,
    SkillMatchResponse,
    SkillResult,
)
from app.services.skillgraph.relationships import skill_relationship_network
from app.services.skillgraph.roadmap import generate_roadmap_task, get_role_roadmap
from app.services.skillgraph.skill_taxonomy import (
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
    "Active API call patterns provide high confidence; package imports alone provide low confidence."
)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def match_skills(
    extracted_skills: List[ExtractedSkill],
    analysis_result: Optional[AnalysisResult],
    target_role: Optional[str] = "all",
) -> SkillMatchResponse:
    """
    Match extracted skills against an optional RepoMind AnalysisResult.
    Synthesizes multi-pattern code evidence, assigns confidence levels,
    derives related skills from the skill network, and generates actionable
    roadmap tasks for required skill gaps.
    """
    import_set: Set[str] = set()
    symbol_list: List[CodeSymbol] = []
    symbol_by_id: Dict[str, CodeSymbol] = {}
    unresolved_calls: List[UnresolvedCall] = []

    if analysis_result is not None:
        for pkg in getattr(analysis_result, "imported_packages", []) or []:
            if isinstance(pkg, str) and pkg.strip():
                import_set.add(pkg.strip().lower())

        symbol_list = list(analysis_result.symbols or [])
        symbol_by_id = {s.id: s for s in symbol_list}
        unresolved_calls = list(analysis_result.unresolved_calls or [])

    required_results: List[SkillResult] = []
    preferred_results: List[SkillResult] = []

    for skill in extracted_skills:
        result = _evaluate_skill(
            skill=skill,
            import_set=import_set,
            symbols=symbol_list,
            symbol_by_id=symbol_by_id,
            unresolved_calls=unresolved_calls,
            target_role=target_role,
        )
        if skill.is_required:
            required_results.append(result)
        else:
            preferred_results.append(result)

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
            "Scan a repository with RepoMind to see code evidence."
        ),
    )

    role_roadmap_raw = get_role_roadmap(target_role)
    role_roadmap_tasks = [
        RoadmapTask(
            task_id=r["task_id"],
            skill_name=r["skill_name"],
            title=r["title"],
            task_title=r.get("task_title", r["title"]),
            difficulty=r["difficulty"],
            estimated_hours=r["estimated_hours"],
            target_role_relevance=r["target_role_relevance"],
            role_relevance=r.get("role_relevance", r["target_role_relevance"]),
            objective=r.get("objective", r["description"]),
            description=r["description"],
            deliverable=r["deliverable"],
            completion_criteria=r["completion_criteria"],
            developed_skills=r["developed_skills"],
            resources=[
                LearningResourceModel(
                    title=res["title"],
                    url=res["url"],
                    provider=res["provider"],
                    resource_type=res["resource_type"],
                )
                for res in r.get("resources", [])
            ],
        )
        for r in role_roadmap_raw
    ]

    return SkillMatchResponse(
        skills_required=required_results,
        skills_preferred=preferred_results,
        role_roadmap=role_roadmap_tasks,
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
    symbol_by_id: Dict[str, CodeSymbol],
    unresolved_calls: List[UnresolvedCall],
    target_role: Optional[str],
) -> SkillResult:
    """Evaluate a single canonical skill across multi-pattern code signals."""
    canonical = skill.canonical_name
    all_aliases = aliases_for(canonical)
    info = get_skill_info(canonical)

    evidence_items: List[EvidenceItem] = []

    # 1. Package import evidence (low confidence by itself)
    import_evidence = _collect_import_evidence(canonical, all_aliases, import_set)
    evidence_items.extend(import_evidence)

    # 2. Direct library call pattern evidence (high confidence)
    call_evidence = _collect_call_pattern_evidence(
        canonical, all_aliases, unresolved_calls, symbol_by_id
    )
    evidence_items.extend(call_evidence)

    # 3. Authored symbol names and docstrings (medium confidence)
    symbol_evidence = _collect_symbol_evidence(canonical, all_aliases, symbols)
    evidence_items.extend(symbol_evidence)

    # 4. Classify evidence tier with safeguards
    tier, explanation = _classify_tier(canonical, evidence_items)

    # 5. Related skills from knowledge graph
    related_skills = skill_relationship_network.get_related_skills(canonical, limit=5)

    # 6. Actionable recommendations & Roadmap tasks (decision 1: required weak/missing first)
    recommendation: Optional[str] = None
    roadmap_task: Optional[RoadmapTask] = None

    if tier in (EvidenceTier.WEAK, EvidenceTier.NONE) and info:
        recommendation = info.recommendation

        # Only required skills generate structured roadmap tasks for MVP
        if skill.is_required:
            raw_task = generate_roadmap_task(canonical, target_role=target_role)
            if raw_task:
                resources = [
                    LearningResourceModel(
                        title=r["title"],
                        url=r["url"],
                        provider=r["provider"],
                        resource_type=r["resource_type"],
                    )
                    for r in raw_task.get("resources", [])
                ]
                roadmap_task = RoadmapTask(
                    task_id=raw_task["task_id"],
                    skill_name=raw_task["skill_name"],
                    title=raw_task["title"],
                    task_title=raw_task.get("task_title", raw_task["title"]),
                    difficulty=raw_task["difficulty"],
                    estimated_hours=raw_task["estimated_hours"],
                    target_role_relevance=raw_task["target_role_relevance"],
                    role_relevance=raw_task.get("role_relevance", raw_task["target_role_relevance"]),
                    objective=raw_task.get("objective", raw_task["description"]),
                    description=raw_task["description"],
                    deliverable=raw_task["deliverable"],
                    completion_criteria=raw_task["completion_criteria"],
                    developed_skills=raw_task["developed_skills"],
                    resources=resources,
                )

    return SkillResult(
        canonical_name=canonical,
        aliases_matched=skill.raw_aliases_found or list({
            a for a in all_aliases if a in (skill.canonical_name, *skill.raw_aliases_found)
        }),
        evidence_tier=tier,
        evidence_items=evidence_items,
        explanation=explanation,
        related_skills=related_skills,
        recommendation=recommendation,
        roadmap_task=roadmap_task,
    )


# ---------------------------------------------------------------------------
# Signal collectors
# ---------------------------------------------------------------------------

def _collect_import_evidence(
    canonical: str,
    all_aliases: List[str],
    import_set: Set[str],
) -> List[EvidenceItem]:
    """Check whether any alias appears in imported_packages."""
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
            confidence=EvidenceConfidence.LOW,
            package=matched_pkg,
            detail=(
                f"Package '{matched_pkg}' was imported in the repository "
                f"(canonical skill: {canonical}). "
                "Import presence alone is low-confidence; see authored code signals below."
            ),
        )
    ]


def _collect_call_pattern_evidence(
    canonical: str,
    all_aliases: List[str],
    unresolved_calls: List[UnresolvedCall],
    symbol_by_id: Dict[str, CodeSymbol],
) -> List[EvidenceItem]:
    """
    Search unresolved external calls for invocations on skill objects (e.g., np.dot, torch.randn).
    Preserves real file paths and line numbers from RepoMind artifacts.
    """
    call_evidence: List[EvidenceItem] = []
    seen_call_keys: Set[Tuple[str, int, str]] = set()

    # Prefixes that indicate library calls (canonical or alias + dot, e.g., 'np.', 'torch.')
    relevant_prefixes: Set[str] = {f"{canonical.lower()}."} | {
        f"{a.lower()}." for a in all_aliases if len(a) >= 2
    }

    for u in unresolved_calls:
        expr = u.call_expression.strip()
        expr_lower = expr.lower()

        # Check if the call expression starts with a known skill prefix
        matched_prefix = any(expr_lower.startswith(p) for p in relevant_prefixes)

        # Or exact function call match for skills named after their call (e.g. pytest.raises)
        if not matched_prefix and "." in expr:
            parts = expr.split(".")
            if parts[0].lower() in [a.lower() for a in all_aliases]:
                matched_prefix = True

        if matched_prefix:
            caller_sym = symbol_by_id.get(u.caller_symbol_id)
            file_path = caller_sym.location.file_path if caller_sym else None
            start_line = caller_sym.location.start_line if caller_sym else None
            end_line = caller_sym.location.end_line if caller_sym else None
            symbol_name = caller_sym.name if caller_sym else None

            dedup_key = (file_path or "", u.line_number, expr)
            if dedup_key in seen_call_keys:
                continue
            seen_call_keys.add(dedup_key)

            call_evidence.append(
                EvidenceItem(
                    kind="call_pattern",
                    confidence=EvidenceConfidence.HIGH,
                    package=canonical,
                    symbol_id=u.caller_symbol_id,
                    symbol_name=symbol_name,
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    line_number=u.line_number,
                    detail=(
                        f"Direct library call invocation '{expr}' detected at line {u.line_number}"
                        + (f" inside symbol '{symbol_name}'." if symbol_name else ".")
                    ),
                )
            )

    return call_evidence


def _collect_symbol_evidence(
    canonical: str,
    all_aliases: List[str],
    symbols: List[CodeSymbol],
) -> List[EvidenceItem]:
    """Search authored symbol names and docstrings for keyword references."""
    info = get_skill_info(canonical)
    jd_keywords = info.jd_keywords if info else []

    name_keywords: Set[str] = {canonical.lower()} | {
        a.lower() for a in all_aliases if len(a) >= 3
    }
    doc_keywords: Set[str] = name_keywords | {kw.lower() for kw in jd_keywords}

    doc_patterns = [
        re.compile(rf"(?i)\b{re.escape(kw)}\b") for kw in doc_keywords if kw
    ]

    evidence: List[EvidenceItem] = []
    seen_symbol_ids: Set[str] = set()
    _TOKEN_SPLIT = re.compile(r"[_\W]+")

    for sym in symbols:
        if sym.id in seen_symbol_ids or sym.symbol_type == "module":
            continue

        name_tokens = {t.lower() for t in _TOKEN_SPLIT.split(sym.name) if t}
        matched_kw = name_keywords & name_tokens

        if matched_kw:
            kw_str = next(iter(matched_kw))
            evidence.append(
                EvidenceItem(
                    kind="symbol",
                    confidence=EvidenceConfidence.MEDIUM,
                    symbol_id=sym.id,
                    symbol_name=sym.name,
                    file_path=sym.location.file_path,
                    start_line=sym.location.start_line,
                    end_line=sym.location.end_line,
                    detail=(
                        f"Authored symbol name '{sym.name}' ({sym.symbol_type}) "
                        f"contains keyword '{kw_str}' referencing '{canonical}'."
                    ),
                )
            )
            seen_symbol_ids.add(sym.id)
            continue

        if sym.docstring:
            doc_matched: Optional[str] = None
            for pat in doc_patterns:
                if pat.search(sym.docstring):
                    doc_matched = pat.pattern
                    break
            if doc_matched:
                evidence.append(
                    EvidenceItem(
                        kind="docstring",
                        confidence=EvidenceConfidence.MEDIUM,
                        symbol_id=sym.id,
                        symbol_name=sym.name,
                        file_path=sym.location.file_path,
                        start_line=sym.location.start_line,
                        end_line=sym.location.end_line,
                        detail=(
                            f"Docstring of '{sym.name}' ({sym.symbol_type}) "
                            f"references '{canonical}'."
                        ),
                    )
                )
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
    Assign evidence tier and generate explainable justification.

    Rules:
    - STRONG:
        - Import present AND at least 1 authored code signal (call pattern, symbol, or docstring).
        - OR two or more independent authored code signals (e.g. call_pattern + symbol, or 2 symbols).
    - WEAK:
        - Exactly one signal (import alone, or single call pattern alone, or single symbol name alone).
    - NONE:
        - Zero evidence items found.
    """
    import_items = [e for e in evidence_items if e.kind == "import"]
    authored_items = [e for e in evidence_items if e.kind in ("call_pattern", "symbol", "docstring")]
    call_patterns = [e for e in evidence_items if e.kind == "call_pattern"]

    has_import = len(import_items) > 0
    authored_count = len(authored_items)
    call_count = len(call_patterns)

    # Strong: Import + authored corroboration
    if has_import and authored_count >= 1:
        detail_msg = f"corroborated by {authored_count} authored code signal(s)"
        if call_count > 0:
            detail_msg += f" including {call_count} direct API invocation(s)"
        explanation = (
            f"Strong evidence: '{canonical}' was imported and {detail_msg}. "
            "Import presence combined with active code authoring demonstrates contextual usage."
        )
        return EvidenceTier.STRONG, explanation

    # Strong: Multiple independent authored code signals (even if import was omitted in partial file scans)
    if authored_count >= 2:
        explanation = (
            f"Strong evidence: {authored_count} authored code signals referencing '{canonical}' "
            "were detected across the repository, indicating active multi-point implementation."
        )
        return EvidenceTier.STRONG, explanation

    # Weak: Import alone
    if has_import and authored_count == 0:
        explanation = (
            f"Weak evidence: '{canonical}' was imported, but no active call invocations, "
            "symbol names, or docstring references were found. "
            "An import alone does not demonstrate active code authorship."
        )
        return EvidenceTier.WEAK, explanation

    # Weak: Single authored signal alone (single API call or single symbol name without corroboration)
    if authored_count == 1:
        item = authored_items[0]
        explanation = (
            f"Weak evidence: a single {item.kind} signal for '{canonical}' was detected "
            f"(in {item.file_path or 'repository'}), but lacked corroborating package imports "
            "or additional symbol implementations."
        )
        return EvidenceTier.WEAK, explanation

    explanation = (
        f"No evidence: no import statements, API invocations, symbol names, "
        f"or docstring references to '{canonical}' were found in the analyzed repository."
    )
    return EvidenceTier.NONE, explanation
