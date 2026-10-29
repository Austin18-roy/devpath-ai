"""
test_skillgraph_matcher.py — Unit tests for evidence collection and tier classification.
"""

import pytest
from app.services.skillgraph.extractor import ExtractedSkill
from app.services.skillgraph.matcher import match_skills
from app.services.skillgraph.models import EvidenceTier
from app.services.repomind.models import (
    AnalysisResult,
    CodeSymbol,
    DependencyEdge,
    SymbolLocation,
    SymbolType,
)


# ---------------------------------------------------------------------------
# Helpers to build test fixtures
# ---------------------------------------------------------------------------

def _make_symbol(
    name: str,
    symbol_type: str = "function",
    file_path: str = "mymodule.py",
    start_line: int = 1,
    end_line: int = 5,
    docstring: str = None,
    parent_id: str = None,
) -> CodeSymbol:
    return CodeSymbol(
        id=f"func:{file_path}::{name}",
        name=name,
        symbol_type=symbol_type,
        location=SymbolLocation(
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            start_col=0,
            end_col=0,
        ),
        parent_id=parent_id,
        docstring=docstring,
    )


def _make_analysis(
    imported_packages: list[str] = None,
    symbols: list[CodeSymbol] = None,
) -> AnalysisResult:
    return AnalysisResult(
        repo_path="/fake/repo",
        files_scanned=1,
        symbols_count=len(symbols or []),
        edges_count=0,
        symbols=symbols or [],
        edges=[],
        unresolved_calls=[],
        diagnostics=[],
        limitations=[],
        imported_packages=imported_packages or [],
    )


def _make_skill(
    canonical: str,
    is_required: bool = True,
    raw_aliases: list[str] = None,
) -> ExtractedSkill:
    return ExtractedSkill(
        canonical_name=canonical,
        is_required=is_required,
        classification_reason="test",
        raw_aliases_found=raw_aliases or [canonical],
    )


def _get_result(response, canonical_name):
    all_results = response.skills_required + response.skills_preferred
    return next((r for r in all_results if r.canonical_name == canonical_name), None)


# ---------------------------------------------------------------------------
# No analysis_result provided
# ---------------------------------------------------------------------------

def test_no_analysis_result_all_tiers_none():
    """When no repo analysis is provided, all skills should be classified as none."""
    skills = [
        _make_skill("numpy", is_required=True),
        _make_skill("docker", is_required=False),
    ]
    response = match_skills(skills, None)
    for r in response.skills_required + response.skills_preferred:
        assert r.evidence_tier == EvidenceTier.NONE, (
            f"{r.canonical_name} should be NONE with no analysis_result"
        )


def test_no_analysis_result_recommendations_present():
    """Even without a repo scan, gap recommendations should be provided."""
    skills = [_make_skill("pytorch", is_required=True)]
    response = match_skills(skills, None)
    pt = _get_result(response, "pytorch")
    assert pt is not None
    assert pt.recommendation is not None and len(pt.recommendation) > 10


def test_no_analysis_result_summary_coverage_note_mentions_no_analysis():
    skills = [_make_skill("numpy")]
    response = match_skills(skills, None)
    assert "no repository analysis" in response.summary.coverage_note.lower()


# ---------------------------------------------------------------------------
# Import-only evidence → WEAK (critical rule)
# ---------------------------------------------------------------------------

def test_import_alone_is_weak_not_strong():
    """
    An import alone MUST NOT produce STRONG evidence.
    This is a core design rule: import presence does not prove proficiency.
    """
    analysis = _make_analysis(imported_packages=["numpy"])
    skills = [_make_skill("numpy")]
    response = match_skills(skills, analysis)
    np_ = _get_result(response, "numpy")
    assert np_ is not None
    assert np_.evidence_tier == EvidenceTier.WEAK, (
        "Import alone must be WEAK, not STRONG"
    )
    assert "import" in np_.explanation.lower()
    assert "alone" in np_.explanation.lower() or "corroboration" in np_.explanation.lower()


def test_import_alone_explanation_mentions_limitation():
    analysis = _make_analysis(imported_packages=["sklearn"])
    skills = [_make_skill("scikit-learn", raw_aliases=["sklearn"])]
    response = match_skills(skills, analysis)
    sk = _get_result(response, "scikit-learn")
    assert sk is not None
    assert sk.evidence_tier == EvidenceTier.WEAK
    # Explanation must mention that import alone is insufficient
    assert "alone" in sk.explanation.lower() or "does not demonstrate" in sk.explanation.lower()


# ---------------------------------------------------------------------------
# Import + symbol/docstring → STRONG
# ---------------------------------------------------------------------------

def test_import_plus_symbol_name_is_strong():
    sym = _make_symbol("train_sklearn_model", file_path="train.py", start_line=10, end_line=30)
    analysis = _make_analysis(imported_packages=["sklearn"], symbols=[sym])
    skills = [_make_skill("scikit-learn", raw_aliases=["sklearn"])]
    response = match_skills(skills, analysis)
    sk = _get_result(response, "scikit-learn")
    assert sk is not None
    assert sk.evidence_tier == EvidenceTier.STRONG


def test_import_plus_docstring_is_strong():
    sym = _make_symbol(
        "fit_model",
        docstring="Trains a model using scikit-learn RandomForestClassifier.",
        file_path="ml.py",
        start_line=5,
        end_line=20,
    )
    analysis = _make_analysis(imported_packages=["sklearn"], symbols=[sym])
    skills = [_make_skill("scikit-learn", raw_aliases=["sklearn"])]
    response = match_skills(skills, analysis)
    sk = _get_result(response, "scikit-learn")
    assert sk is not None
    assert sk.evidence_tier == EvidenceTier.STRONG


# ---------------------------------------------------------------------------
# Two or more symbol/docstring items (no import) → STRONG
# ---------------------------------------------------------------------------

def test_two_symbol_references_without_import_is_strong():
    sym1 = _make_symbol("train_numpy_array", file_path="a.py", start_line=1, end_line=5)
    sym2 = _make_symbol("reshape_numpy_data", file_path="b.py", start_line=10, end_line=15)
    analysis = _make_analysis(imported_packages=[], symbols=[sym1, sym2])
    skills = [_make_skill("numpy")]
    response = match_skills(skills, analysis)
    np_ = _get_result(response, "numpy")
    assert np_ is not None
    assert np_.evidence_tier == EvidenceTier.STRONG


# ---------------------------------------------------------------------------
# Single symbol match (no import) → WEAK
# ---------------------------------------------------------------------------

def test_single_symbol_name_no_import_is_weak():
    sym = _make_symbol("pytorch_training_loop", file_path="train.py", start_line=1, end_line=50)
    analysis = _make_analysis(imported_packages=[], symbols=[sym])
    skills = [_make_skill("pytorch")]
    response = match_skills(skills, analysis)
    pt = _get_result(response, "pytorch")
    assert pt is not None
    assert pt.evidence_tier == EvidenceTier.WEAK


# ---------------------------------------------------------------------------
# No evidence
# ---------------------------------------------------------------------------

def test_no_evidence_tier_is_none():
    analysis = _make_analysis(imported_packages=["pandas"], symbols=[])
    skills = [_make_skill("pytorch")]  # pytorch not in imports or symbols
    response = match_skills(skills, analysis)
    pt = _get_result(response, "pytorch")
    assert pt is not None
    assert pt.evidence_tier == EvidenceTier.NONE


def test_none_tier_has_recommendation():
    analysis = _make_analysis()
    skills = [_make_skill("docker", is_required=False)]
    response = match_skills(skills, analysis)
    docker = _get_result(response, "docker")
    assert docker is not None
    assert docker.evidence_tier == EvidenceTier.NONE
    assert docker.recommendation is not None


# ---------------------------------------------------------------------------
# Evidence item fields — real paths and line numbers
# ---------------------------------------------------------------------------

def test_symbol_evidence_item_has_real_file_path_and_lines():
    sym = _make_symbol(
        "pytorch_model",
        file_path="models/resnet.py",
        start_line=42,
        end_line=80,
    )
    analysis = _make_analysis(imported_packages=["torch"], symbols=[sym])
    skills = [_make_skill("pytorch", raw_aliases=["torch"])]
    response = match_skills(skills, analysis)
    pt = _get_result(response, "pytorch")
    assert pt is not None
    symbol_items = [e for e in pt.evidence_items if e.kind == "symbol"]
    assert len(symbol_items) >= 1
    item = symbol_items[0]
    assert item.file_path == "models/resnet.py"
    assert item.start_line == 42
    assert item.end_line == 80
    assert item.symbol_id == "func:models/resnet.py::pytorch_model"


def test_import_evidence_item_has_package_name():
    analysis = _make_analysis(imported_packages=["pandas"])
    skills = [_make_skill("pandas")]
    response = match_skills(skills, analysis)
    pd_ = _get_result(response, "pandas")
    assert pd_ is not None
    import_items = [e for e in pd_.evidence_items if e.kind == "import"]
    assert len(import_items) == 1
    assert import_items[0].package == "pandas"


# ---------------------------------------------------------------------------
# Alias matching
# ---------------------------------------------------------------------------

def test_alias_pd_matches_pandas_import():
    analysis = _make_analysis(imported_packages=["pd"])
    skills = [_make_skill("pandas", raw_aliases=["pd"])]
    response = match_skills(skills, analysis)
    pd_ = _get_result(response, "pandas")
    assert pd_ is not None
    # pd is an alias for pandas in SKILL_ALIASES
    assert pd_.evidence_tier in (EvidenceTier.WEAK, EvidenceTier.STRONG)


# ---------------------------------------------------------------------------
# Required / preferred split in response
# ---------------------------------------------------------------------------

def test_required_preferred_split_in_response():
    skills = [
        _make_skill("numpy", is_required=True),
        _make_skill("docker", is_required=False),
    ]
    response = match_skills(skills, None)
    req_names = {r.canonical_name for r in response.skills_required}
    pref_names = {r.canonical_name for r in response.skills_preferred}
    assert "numpy" in req_names
    assert "docker" in pref_names


# ---------------------------------------------------------------------------
# Summary counts
# ---------------------------------------------------------------------------

def test_summary_counts_match_results():
    sym = _make_symbol("torch_train", file_path="train.py")
    analysis = _make_analysis(imported_packages=["torch"], symbols=[sym])
    skills = [
        _make_skill("pytorch", is_required=True, raw_aliases=["torch"]),
        _make_skill("docker", is_required=False),
    ]
    response = match_skills(skills, analysis)
    all_results = response.skills_required + response.skills_preferred
    strong = sum(1 for r in all_results if r.evidence_tier == EvidenceTier.STRONG)
    weak = sum(1 for r in all_results if r.evidence_tier == EvidenceTier.WEAK)
    none_ = sum(1 for r in all_results if r.evidence_tier == EvidenceTier.NONE)
    assert response.summary.strong_evidence_count == strong
    assert response.summary.weak_evidence_count == weak
    assert response.summary.no_evidence_count == none_


# ---------------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------------

def test_disclaimer_present_and_non_empty():
    response = match_skills([], None)
    assert len(response.disclaimer) > 20
    assert "static" in response.disclaimer.lower() or "analysis" in response.disclaimer.lower()


# ---------------------------------------------------------------------------
# False positive guard: generic symbol names should not match unrelated skills
# ---------------------------------------------------------------------------

def test_generic_symbol_name_does_not_false_positive():
    """
    A function named 'train' should not match 'pytorch' or 'tensorflow'.
    Only names containing actual skill keywords get matched.
    """
    sym = _make_symbol("train", file_path="generic.py")
    analysis = _make_analysis(symbols=[sym])
    skills = [_make_skill("pytorch"), _make_skill("tensorflow")]
    response = match_skills(skills, analysis)
    pt = _get_result(response, "pytorch")
    tf = _get_result(response, "tensorflow")
    # Neither should have symbol evidence from a generic 'train' function
    for r in [pt, tf]:
        if r is not None:
            symbol_items = [e for e in r.evidence_items if e.kind == "symbol"]
            assert len(symbol_items) == 0, (
                f"Generic 'train' symbol should not produce evidence for {r.canonical_name}"
            )

