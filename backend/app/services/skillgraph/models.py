"""
models.py — Pydantic request and response models for the SkillGraph API.

All models are intentionally strict (no arbitrary extra fields) to prevent
client-supplied data from silently passing unexpected fields through.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.services.repomind.models import AnalysisResult


# ---------------------------------------------------------------------------
# Evidence tier
# ---------------------------------------------------------------------------

class EvidenceTier(str, Enum):
    """
    Three-tier evidence classification.

    STRONG: Import found AND at least one corroborating symbol/docstring, OR
            two or more independent symbol/docstring references.
    WEAK:   Import found with no corroboration, OR exactly one symbol/docstring
            reference with no import.
    NONE:   No evidence found in the repository.

    An import alone is NEVER classified as STRONG.
    """
    STRONG = "strong"
    WEAK = "weak"
    NONE = "none"


# ---------------------------------------------------------------------------
# Evidence item
# ---------------------------------------------------------------------------

class EvidenceItem(BaseModel):
    """A single piece of evidence linking a skill to the analyzed repository."""

    model_config = {"extra": "forbid"}

    kind: str = Field(
        ...,
        description="Type of evidence: 'import', 'symbol', or 'docstring'.",
    )
    package: Optional[str] = Field(
        None,
        description="Root package name as written in the import statement (kind='import' only).",
    )
    symbol_id: Optional[str] = Field(
        None,
        description="Stable symbol ID from AnalysisResult (kind='symbol'/'docstring' only).",
    )
    symbol_name: Optional[str] = Field(
        None,
        description="Human-readable symbol name (kind='symbol'/'docstring' only).",
    )
    file_path: Optional[str] = Field(
        None,
        description="Repository-relative source file path.",
    )
    start_line: Optional[int] = Field(
        None,
        description="1-based starting line number of the symbol.",
    )
    end_line: Optional[int] = Field(
        None,
        description="1-based ending line number of the symbol.",
    )
    line_number: Optional[int] = Field(
        None,
        description="Exact line number (used for import evidence when available).",
    )
    detail: str = Field(
        ...,
        description="Human-readable explanation of this evidence item.",
    )


# ---------------------------------------------------------------------------
# Per-skill result
# ---------------------------------------------------------------------------

class SkillResult(BaseModel):
    """Evidence report for a single canonical skill."""

    model_config = {"extra": "forbid"}

    canonical_name: str = Field(
        ...,
        description="Canonical skill name from the taxonomy (e.g. 'scikit-learn').",
    )
    aliases_matched: List[str] = Field(
        default_factory=list,
        description="Raw alias strings found in the job description for this skill.",
    )
    evidence_tier: EvidenceTier = Field(
        ...,
        description="Classification tier: 'strong', 'weak', or 'none'.",
    )
    evidence_items: List[EvidenceItem] = Field(
        default_factory=list,
        description="All evidence items found in the repository for this skill.",
    )
    explanation: str = Field(
        ...,
        description="Plain-English explanation of why this tier was assigned.",
    )
    recommendation: Optional[str] = Field(
        None,
        description=(
            "Actionable next step to strengthen evidence for this skill. "
            "Only present when tier is 'weak' or 'none'."
        ),
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class MatchSummary(BaseModel):
    """Aggregate counts across all skill results."""

    model_config = {"extra": "forbid"}

    required_count: int = Field(..., description="Number of required skills extracted.")
    preferred_count: int = Field(..., description="Number of preferred skills extracted.")
    strong_evidence_count: int = Field(..., description="Skills with strong evidence.")
    weak_evidence_count: int = Field(..., description="Skills with weak evidence.")
    no_evidence_count: int = Field(..., description="Skills with no evidence.")
    coverage_note: str = Field(
        ...,
        description="Contextual note about the scope and limitations of this analysis.",
    )


# ---------------------------------------------------------------------------
# Request / Response
# ---------------------------------------------------------------------------

class SkillMatchRequest(BaseModel):
    """Request body for POST /api/v1/skillgraph/match."""

    model_config = {"extra": "forbid"}

    job_description: str = Field(
        ...,
        min_length=20,
        max_length=10_000,
        description=(
            "Raw plain-text job description (20–10,000 characters). "
            "Paste the full text; markdown headers are supported."
        ),
    )
    analysis_result: Optional[AnalysisResult] = Field(
        None,
        description=(
            "Optional RepoMind AnalysisResult from a prior repository scan. "
            "If omitted, all skills are classified as 'none' and recommendations "
            "are still generated."
        ),
    )


class SkillMatchResponse(BaseModel):
    """Response body for POST /api/v1/skillgraph/match."""

    model_config = {"extra": "forbid"}

    skills_required: List[SkillResult] = Field(
        default_factory=list,
        description="Required skills extracted from the job description, in alphabetical order.",
    )
    skills_preferred: List[SkillResult] = Field(
        default_factory=list,
        description="Preferred skills extracted from the job description, in alphabetical order.",
    )
    summary: MatchSummary = Field(..., description="Aggregate evidence counts and coverage note.")
    disclaimer: str = Field(
        ...,
        description=(
            "Fixed disclaimer clarifying that SkillGraph reflects static code analysis only, "
            "not personal skill level or hiring suitability."
        ),
    )

