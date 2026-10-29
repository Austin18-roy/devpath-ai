"""
extractor.py — Job-description skill extraction for SkillGraph.

Design goals:
- Deterministic: same input always produces the same output.
- No external API calls, no ML models required.
- Transparent: every extracted skill carries the raw aliases found and the
  classification reason (required / preferred + detection signal).
- Conservative: skills whose required/preferred status is ambiguous default to
  "required" so users never silently under-count required skills.

Extraction algorithm:
1. Split the JD text into labelled sections by heading detection.
2. Within each section, search sentence-by-sentence for inline signals
   (e.g. "must", "preferred").
3. Match all skill aliases from the taxonomy against each sentence using
   whole-word regex.
4. Normalise matched aliases to canonical names and de-duplicate.
5. Return a list of ExtractedSkill dataclasses, one per canonical skill.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from app.services.skillgraph.skill_taxonomy import (
    SKILL_ALIASES,
    SKILL_METADATA,
    aliases_for,
    normalise_alias,
)


# ---------------------------------------------------------------------------
# Section heading patterns
# ---------------------------------------------------------------------------

_REQUIRED_HEADING_RE = re.compile(
    r"(?i)^(?:(?:(?:job|role|key)\s+)?requirements?|qualifications?|"
    r"(?:required|essential|minimum|basic|core|mandatory)\s+(?:qualifications?|skills?|requirements?|experience|competencies|background)?|"
    r"required|"
    r"must[- ]have(?:\s+(?:skills?|qualifications?|requirements?))?|"
    r"what\s+you(?:\x27ll|\s+will)?\s+(?:need|must\s+have)|"
    r"you\s+(?:must|need|will\s+need)"
    r")$"
)

_PREFERRED_HEADING_RE = re.compile(
    r"(?i)^(?:preferences?|"
    r"(?:preferred|desired|optional|additional|bonus|advantageous)\s+(?:qualifications?|skills?|requirements?|experience|competencies|background|points?)?|"
    r"preferred|"
    r"nice[- ]to[- ]have(?:\s+(?:skills?|qualifications?|requirements?))?|"
    r"good[- ]to[- ]have(?:\s+(?:skills?|qualifications?|requirements?))?|"
    r"bonus(?:\s+(?:points?|skills?|qualifications?))?|"
    r"(?:an?\s+)?ideal\s+(?:candidate|qualifications?|profile)?|"
    r"pluses?|plus|"
    r"assets?"
    r")$"
)


def _is_bullet_item(line: str) -> bool:
    """Check if a line begins with a list/bullet marker (should not be treated as a heading)."""
    return bool(re.match(r"^\s*(?:[-*+•]|\d+[.)])\s+", line))


def _clean_heading(line: str) -> str:
    """Normalize a potential heading line by stripping markdown formatting and trailing punctuation."""
    s = line.strip()
    # Strip markdown headers: #, ##, ###, ####, etc.
    s = re.sub(r"^#{1,6}\s*", "", s)
    # Strip enclosing markdown bold / italics: **text**, __text__, *text*
    s = re.sub(r"^(\*\*|\*|__)(.*?)\1$", r"\2", s).strip()
    # Strip trailing colons, dashes, and whitespace
    s = re.sub(r"[\s:\-]+$", "", s).strip()
    return s



# ---------------------------------------------------------------------------
# Inline sentence-level signal patterns
# ---------------------------------------------------------------------------

_REQUIRED_INLINE_RE = re.compile(
    r"(?i)\b(?:required|must|essential|mandatory|need|you.must)\b"
)

_PREFERRED_INLINE_RE = re.compile(
    r"(?i)\b(?:preferred|nice.to.have|bonus|ideally|plus|advantage|advantageous)\b"
)


# ---------------------------------------------------------------------------
# Precompile a whole-word regex for every alias
# ---------------------------------------------------------------------------
# Aliases that contain only word characters get word-boundary anchors.
# Aliases with dots/dashes (e.g. "scikit-learn", "google.cloud") get a
# lookahead/lookbehind that requires a non-alphanumeric boundary or
# start/end of string.

def _build_alias_pattern(alias: str) -> re.Pattern:
    escaped = re.escape(alias)
    if re.fullmatch(r"[\w]+", alias):
        return re.compile(rf"(?i)\b{escaped}\b")
    else:
        return re.compile(rf"(?i)(?<![a-zA-Z0-9_]){escaped}(?![a-zA-Z0-9_])")


# Map alias (lower) -> compiled pattern
_ALIAS_PATTERNS: Dict[str, re.Pattern] = {
    alias: _build_alias_pattern(alias) for alias in SKILL_ALIASES
}


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------

@dataclass
class ExtractedSkill:
    """One canonical skill extracted from a job description."""
    canonical_name: str
    is_required: bool            # True = required, False = preferred
    classification_reason: str   # Human-readable explanation of the classification
    raw_aliases_found: List[str] = field(default_factory=list)
    # JD keyword matches (non-package phrases like "machine learning")
    jd_keyword_matches: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal section model
# ---------------------------------------------------------------------------

@dataclass
class _Section:
    label: str           # "required" | "preferred" | "unknown"
    text: str


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_skills(job_description: str) -> List[ExtractedSkill]:
    """
    Parse a raw job description and return one ExtractedSkill per canonical skill found.

    The result list is deduplicated: if the same canonical skill appears in both
    required and preferred sections, it is returned once as 'required'.

    Args:
        job_description: Raw plain-text or lightly formatted job description.

    Returns:
        List of ExtractedSkill, sorted required-first then alphabetically.
    """
    sections = _split_into_sections(job_description)

    # canonical_name -> ExtractedSkill (required wins over preferred)
    collected: Dict[str, ExtractedSkill] = {}

    for section in sections:
        _extract_from_section(section, collected)

    results = sorted(
        collected.values(),
        key=lambda s: (not s.is_required, s.canonical_name),
    )
    return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _split_into_sections(text: str) -> List[_Section]:
    """
    Split the JD text into sections by detecting heading lines.
    Unclassified content (before any heading, or under unrecognised headings)
    goes into 'unknown' sections.
    """
    lines = text.splitlines()
    sections: List[_Section] = []
    current_label = "unknown"
    current_lines: List[str] = []

    for line in lines:
        if not _is_bullet_item(line):
            cleaned = _clean_heading(line)
            if cleaned and _REQUIRED_HEADING_RE.match(cleaned):
                if current_lines and any(l.strip() for l in current_lines):
                    sections.append(_Section(label=current_label, text="\n".join(current_lines)))
                current_label = "required"
                current_lines = []
                continue
            elif cleaned and _PREFERRED_HEADING_RE.match(cleaned):
                if current_lines and any(l.strip() for l in current_lines):
                    sections.append(_Section(label=current_label, text="\n".join(current_lines)))
                current_label = "preferred"
                current_lines = []
                continue

        current_lines.append(line)

    if current_lines and any(l.strip() for l in current_lines):
        sections.append(_Section(label=current_label, text="\n".join(current_lines)))

    return sections


def _classify_sentence(sentence: str, section_label: str) -> Tuple[bool, str]:
    """
    Determine (is_required, reason_str) for a sentence within a section.

    Priority:
    1. Section heading label (required / preferred)
    2. Inline required/preferred signal words
    3. Conservative default: required
    """
    if section_label == "required":
        return True, "Listed under a required/qualifications section heading"
    if section_label == "preferred":
        if _REQUIRED_INLINE_RE.search(sentence) and not _PREFERRED_INLINE_RE.search(sentence):
            return True, "Sentence contains an explicit required/must signal word"
        return False, "Listed under a preferred/nice-to-have section heading"
    # Inline signals
    if _REQUIRED_INLINE_RE.search(sentence):
        return True, "Sentence contains a required/must signal word"
    if _PREFERRED_INLINE_RE.search(sentence):
        return False, "Sentence contains a preferred/nice-to-have signal word"
    # Conservative default
    return True, "No required/preferred signal found — defaulting to required (conservative)"


def _extract_from_section(section: _Section, collected: Dict[str, "ExtractedSkill"]) -> None:
    """
    Scan every sentence in a section for alias matches and update `collected`.
    """
    # Split into rough sentences / bullet points
    sentences = _split_sentences(section.text)

    for sentence in sentences:
        if not sentence.strip():
            continue

        is_required, reason = _classify_sentence(sentence, section.label)

        # Find all alias matches in this sentence
        matched_aliases: List[str] = []
        for alias, pattern in _ALIAS_PATTERNS.items():
            if pattern.search(sentence):
                matched_aliases.append(alias)

        # Also check taxonomy JD keywords (non-package phrases)
        jd_keyword_hits: List[str] = []
        for canonical, info in SKILL_METADATA.items():
            for kw in info.jd_keywords:
                kw_pattern = re.compile(rf"(?i)\b{re.escape(kw)}\b")
                if kw_pattern.search(sentence):
                    jd_keyword_hits.append((canonical, kw))

        # Normalise aliases to canonicals
        canonical_hits: Dict[str, List[str]] = {}  # canonical -> list of matched aliases
        for alias in matched_aliases:
            canon = normalise_alias(alias)
            if canon:
                canonical_hits.setdefault(canon, []).append(alias)

        # Add JD keyword hits that didn't already have an alias match
        for canonical, kw in jd_keyword_hits:
            if canonical not in canonical_hits:
                canonical_hits.setdefault(canonical, [])

        # Merge into collected dict
        for canonical, raw_aliases in canonical_hits.items():
            if canonical in collected:
                existing = collected[canonical]
                # Required wins over preferred
                if is_required and not existing.is_required:
                    existing.is_required = True
                    existing.classification_reason = reason
                # Accumulate new aliases
                for a in raw_aliases:
                    if a not in existing.raw_aliases_found:
                        existing.raw_aliases_found.append(a)
            else:
                # Find any jd_keyword hits for this canonical
                kw_hits = [kw for (c, kw) in jd_keyword_hits if c == canonical]
                collected[canonical] = ExtractedSkill(
                    canonical_name=canonical,
                    is_required=is_required,
                    classification_reason=reason,
                    raw_aliases_found=list(raw_aliases),
                    jd_keyword_matches=kw_hits,
                )


def _split_sentences(text: str) -> List[str]:
    """
    Split text into sentence-like units suitable for inline signal detection.
    Handles bullet points, line breaks, and period-delimited sentences.
    """
    # First split on newlines (covers bullet lists)
    parts: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Further split long lines on sentence terminators
        sub_parts = re.split(r"(?<=[.!?])\s+", line)
        parts.extend(sub_parts)
    return parts

