"""
test_skillgraph_pattern_matcher.py — Tests for call-pattern evidence, confidence ratings, and roadmap generation.
"""

from app.services.skillgraph.extractor import ExtractedSkill
from app.services.skillgraph.matcher import match_skills
from app.services.skillgraph.models import EvidenceConfidence, EvidenceTier
from app.services.repomind.models import (
    AnalysisResult,
    CodeSymbol,
    SymbolLocation,
    UnresolvedCall,
)


def _make_symbol(name: str, file_path: str = "app.py", start_line: int = 1, end_line: int = 10):
    return CodeSymbol(
        id=f"func:{file_path}::{name}",
        name=name,
        symbol_type="function",
        location=SymbolLocation(
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            start_col=0,
            end_col=0,
        ),
        parent_id=None,
        docstring=None,
    )


def _make_call(expr: str, caller_id: str, line: int = 5):
    return UnresolvedCall(
        caller_symbol_id=caller_id,
        call_expression=expr,
        line_number=line,
        reason="External call",
    )


def test_api_call_pattern_gets_high_confidence():
    sym = _make_symbol("run_inference", file_path="model.py", start_line=1, end_line=15)
    call = _make_call("torch.nn.Linear", sym.id, line=7)
    analysis = AnalysisResult(
        repo_path="/test",
        files_scanned=1,
        symbols_count=1,
        edges_count=0,
        symbols=[sym],
        edges=[],
        unresolved_calls=[call],
        diagnostics=[],
        limitations=[],
        imported_packages=[],
    )
    skill = ExtractedSkill(canonical_name="pytorch", is_required=True, classification_reason="test", raw_aliases_found=["pytorch"])

    response = match_skills([skill], analysis)
    res = response.skills_required[0]

    # Verify high confidence call_pattern item
    call_items = [e for e in res.evidence_items if e.kind == "call_pattern"]
    assert len(call_items) == 1
    assert call_items[0].confidence == EvidenceConfidence.HIGH
    assert call_items[0].file_path == "model.py"
    assert call_items[0].line_number == 7


def test_api_call_alone_is_weak_evidence():
    """Safeguard: an isolated API invocation alone must not prove strong proficiency."""
    sym = _make_symbol("calc", file_path="math.py", start_line=1, end_line=5)
    call = _make_call("np.dot", sym.id, line=3)
    analysis = AnalysisResult(
        repo_path="/test",
        files_scanned=1,
        symbols_count=1,
        edges_count=0,
        symbols=[sym],
        edges=[],
        unresolved_calls=[call],
        diagnostics=[],
        limitations=[],
        imported_packages=[],
    )
    skill = ExtractedSkill(canonical_name="numpy", is_required=True, classification_reason="test", raw_aliases_found=["numpy"])

    response = match_skills([skill], analysis)
    res = response.skills_required[0]
    # Single signal without import or symbol token match -> WEAK
    assert res.evidence_tier == EvidenceTier.WEAK
    assert "single call_pattern" in res.explanation.lower() or "weak" in res.explanation.lower()


def test_import_plus_api_call_is_strong_evidence():
    sym = _make_symbol("run_job", file_path="worker.py", start_line=1, end_line=20)
    call = _make_call("torch.randn", sym.id, line=10)
    analysis = AnalysisResult(
        repo_path="/test",
        files_scanned=1,
        symbols_count=1,
        edges_count=0,
        symbols=[sym],
        edges=[],
        unresolved_calls=[call],
        diagnostics=[],
        limitations=[],
        imported_packages=["torch"],
    )
    skill = ExtractedSkill(canonical_name="pytorch", is_required=True, classification_reason="test", raw_aliases_found=["pytorch"])

    response = match_skills([skill], analysis)
    res = response.skills_required[0]
    assert res.evidence_tier == EvidenceTier.STRONG
    assert "imported" in res.explanation.lower()
    assert "invocation" in res.explanation.lower() or "authored" in res.explanation.lower()


def test_roadmap_task_generated_for_weak_required_skill():
    skill = ExtractedSkill(canonical_name="fastapi", is_required=True, classification_reason="test", raw_aliases_found=["fastapi"])
    response = match_skills([skill], None, target_role="aiml_engineer")
    res = response.skills_required[0]

    assert res.evidence_tier == EvidenceTier.NONE
    assert res.roadmap_task is not None
    assert res.roadmap_task.skill_name == "fastapi"
    assert "aiml" in res.roadmap_task.target_role_relevance.lower() or "model" in res.roadmap_task.target_role_relevance.lower()
    assert len(res.roadmap_task.completion_criteria) >= 3
    assert len(res.roadmap_task.resources) >= 1
    assert "fastapi.tiangolo.com" in res.roadmap_task.resources[0].url


def test_roadmap_task_omitted_for_preferred_skill():
    """Decision 1: Generate structured mini-projects for missing/weak required skills first."""
    skill = ExtractedSkill(canonical_name="docker", is_required=False, classification_reason="test", raw_aliases_found=["docker"])
    response = match_skills([skill], None, target_role="all")
    res = response.skills_preferred[0]

    assert res.evidence_tier == EvidenceTier.NONE
    assert res.recommendation is not None  # Recommendation text exists
    assert res.roadmap_task is None  # But roadmap task is None for preferred


def test_related_skills_populated():
    skill = ExtractedSkill(canonical_name="pytorch", is_required=True, classification_reason="test", raw_aliases_found=["pytorch"])
    response = match_skills([skill], None)
    res = response.skills_required[0]

    assert len(res.related_skills) > 0
    assert any(s in res.related_skills for s in ["numpy", "deep-learning", "hugging-face", "torchvision"])

