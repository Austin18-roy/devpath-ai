"""
skillgraph.py — FastAPI router for the SkillGraph job-description skill matcher.

Endpoint: POST /api/v1/skillgraph/match

Security notes:
- No repository paths are accepted; SkillGraph receives a pre-built AnalysisResult.
- The AnalysisResult is treated as untrusted client data: only Pydantic-validated
  fields are accessed. No code from the repository is executed.
- Job descriptions are processed statelessly; nothing is persisted.
- Input size is bounded by SkillMatchRequest field validators (max 10,000 chars).
"""

from fastapi import APIRouter

from app.services.skillgraph.extractor import extract_skills
from app.services.skillgraph.matcher import match_skills
from app.services.skillgraph.models import SkillMatchRequest, SkillMatchResponse

router = APIRouter()


@router.post(
    "/match",
    response_model=SkillMatchResponse,
    summary="Match job description skills against repository evidence",
    description=(
        "Extracts required and preferred skills from a job description, "
        "then searches an optional RepoMind AnalysisResult for corroborating "
        "code evidence (imports, AST call patterns, symbol definitions, docstrings). "
        "Returns per-skill evidence tiers (strong/weak/none), confidence ratings, "
        "related skills from the knowledge network, and personalized career roadmap tasks "
        "tailored to the target role. "
        "No repository code is executed; analysis is purely static."
    ),
)
async def match_job_skills(request: SkillMatchRequest) -> SkillMatchResponse:
    extracted = extract_skills(request.job_description)
    return match_skills(
        extracted_skills=extracted,
        analysis_result=request.analysis_result,
        target_role=request.target_role,
    )

