from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.services.repomind.models import (
    AnalysisResult,
    AnalyzeRequest,
    ChangeImpactReport,
    ImpactRequest,
)
from app.services.repomind.parser import RepoMindParser
from app.services.repomind.graph import RepoDependencyGraph
from app.services.repomind.security import (
    RepositorySecurityError,
    validate_repository_path,
)

router = APIRouter()


def get_effective_allowed_roots() -> List[str]:
    """
    Returns allowed repository roots.
    Falls back to current workspace base directory to prevent arbitrary filesystem traversal.
    """
    if settings.ALLOWED_REPO_ROOTS:
        return [str(r) for r in settings.ALLOWED_REPO_ROOTS]
    
    # Safe default: Allow DevPath AI repository and its parent workspace directory
    current_repo = Path(__file__).resolve().parents[4]
    return [str(current_repo)]


@router.post(
    "/analyze",
    response_model=AnalysisResult,
    summary="Analyze a Python repository",
    description="Parses Python source files using AST, extracts symbols, imports, and dependency calls.",
)
async def analyze_repository(request: AnalyzeRequest) -> AnalysisResult:
    allowed_roots = get_effective_allowed_roots()
    try:
        validated_path = validate_repository_path(request.repo_path, allowed_roots=allowed_roots)
    except RepositorySecurityError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )

    parser = RepoMindParser(
        repo_path=validated_path,
        max_files=settings.MAX_SCAN_FILES,
        max_file_size_bytes=settings.MAX_FILE_SIZE_BYTES,
    )
    return parser.parse_repository()


@router.post(
    "/impact",
    response_model=ChangeImpactReport,
    summary="Analyze change impact for a symbol",
    description="Evaluates direct and transitive upstream callers affected by modifying a target symbol.",
)
async def analyze_change_impact(request: ImpactRequest) -> ChangeImpactReport:
    allowed_roots = get_effective_allowed_roots()
    try:
        validated_path = validate_repository_path(request.repo_path, allowed_roots=allowed_roots)
    except RepositorySecurityError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )

    parser = RepoMindParser(
        repo_path=validated_path,
        max_files=settings.MAX_SCAN_FILES,
        max_file_size_bytes=settings.MAX_FILE_SIZE_BYTES,
    )
    analysis = parser.parse_repository()
    graph = RepoDependencyGraph(analysis)
    return graph.get_change_impact(request.symbol_id)

