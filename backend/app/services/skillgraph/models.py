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
# Evidence tier and confidence
# ---------------------------------------------------------------------------

class EvidenceTier(str, Enum):
    """
    Three-tier evidence classification.

    STRONG: Authored code evidence corroborated by an import or multiple
            independent authored code signals.
    WEAK:   Single signal only (e.g. import alone, single call pattern alone,
            or single isolated symbol name).
    NONE:   No evidence found in the repository.

    An import alone or an isolated API invocation alone is NEVER classified as STRONG.
    """
    STRONG = "strong"
    WEAK = "weak"
    NONE = "none"


class EvidenceConfidence(str, Enum):
    """
    Quality and certainty of an individual evidence artifact.

    HIGH:   Direct method/API call invocation (e.g., `torch.nn.Linear`, `pd.read_csv`)
            or framework base-class inheritance.
    MEDIUM: Authored symbol name token match or descriptive docstring reference.
    LOW:    Top-level package import alone (indicates library inclusion, not authorship).
    NONE:   No matching evidence found.
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


# ---------------------------------------------------------------------------
# Learning resources & Roadmap models
# ---------------------------------------------------------------------------

class LearningResourceModel(BaseModel):
    """Verified free documentation or learning material for a skill."""

    model_config = {"extra": "forbid"}

    title: str = Field(..., description="Resource title")
    url: str = Field(..., description="Verified HTTPS URL")
    provider: str = Field(..., description="Organization or maintainer (e.g., Python Software Foundation)")
    resource_type: str = Field(..., description="Resource format: 'official_docs', 'tutorial', 'handbook'")


class RoadmapTask(BaseModel):
    """Actionable mini-project roadmap task for a specific skill gap."""

    model_config = {"extra": "forbid"}

    task_id: str = Field(..., description="Unique task identifier")
    skill_name: str = Field(..., description="Canonical skill name")
    title: str = Field(..., description="Concise mini-project title")
    task_title: Optional[str] = Field(None, description="Frontend alias for title")
    difficulty: str = Field(..., description="Difficulty rating: 'Beginner', 'Intermediate', 'Advanced'")
    estimated_hours: int = Field(..., description="Estimated completion time in hours (typically 2-4 hours)")
    target_role_relevance: str = Field(..., description="Why this skill matters for the specified target career role")
    role_relevance: Optional[str] = Field(None, description="Frontend alias for target_role_relevance")
    objective: Optional[str] = Field(None, description="What the learner should accomplish in this project")
    description: str = Field(..., description="Step-by-step description of what to implement")
    deliverable: str = Field(..., description="Tangible portfolio deliverable (script, test suite, config)")
    completion_criteria: List[str] = Field(default_factory=list, description="Measurable completion checklist")
    developed_skills: List[str] = Field(default_factory=list, description="Complementary skills exercised by this task")
    resources: List[LearningResourceModel] = Field(default_factory=list, description="Verified free learning resources")


# ---------------------------------------------------------------------------
# Evidence item
# ---------------------------------------------------------------------------

class EvidenceItem(BaseModel):
    """A single piece of evidence linking a skill to the analyzed repository."""

    model_config = {"extra": "forbid"}

    kind: str = Field(
        ...,
        description="Type of evidence: 'import', 'call_pattern', 'symbol', or 'docstring'.",
    )
    confidence: EvidenceConfidence = Field(
        EvidenceConfidence.MEDIUM,
        description="Confidence/quality level of this evidence item.",
    )
    package: Optional[str] = Field(
        None,
        description="Root package name as written in the import statement.",
    )
    symbol_id: Optional[str] = Field(
        None,
        description="Stable symbol ID from AnalysisResult.",
    )
    symbol_name: Optional[str] = Field(
        None,
        description="Human-readable symbol name.",
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
        description="Exact line number (used for import or call_pattern evidence).",
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
    related_skills: List[str] = Field(
        default_factory=list,
        description="Ecosystem skills closely related to this technology from the skill relationship network.",
    )
    recommendation: Optional[str] = Field(
        None,
        description=(
            "Actionable next step to strengthen evidence for this skill. "
            "Only present when tier is 'weak' or 'none'."
        ),
    )
    roadmap_task: Optional[RoadmapTask] = Field(
        None,
        description="Personalized practical mini-project for weak or missing skills.",
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
    target_role: Optional[str] = Field(
        "all",
        description="Target career role for tailoring roadmap tasks: 'all', 'aiml_engineer', 'genai_engineer', 'sde'.",
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
    role_roadmap: List[RoadmapTask] = Field(
        default_factory=list,
        description="Intended role-tailored portfolio roadmap mini-projects.",
    )
    summary: MatchSummary = Field(..., description="Aggregate evidence counts and coverage note.")
    disclaimer: str = Field(
        ...,
        description=(
            "Fixed disclaimer clarifying that SkillGraph reflects static code analysis only, "
            "not personal skill level or hiring suitability."
        ),
    )
