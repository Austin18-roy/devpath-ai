"""
test_skillgraph_api.py — Integration tests for POST /api/v1/skillgraph/match.
Uses the FastAPI TestClient from conftest.py (same pattern as repomind tests).
"""

import pytest
from pathlib import Path

FIXTURE_ROOT = str(Path(__file__).parent / "fixtures" / "sample_repo")

# A realistic AIML/SDE job description for integration tests
SAMPLE_JD_REQUIRED = """
Requirements:
- Strong proficiency with Python and numpy for data manipulation
- Experience building ML models using sklearn or scikit-learn
- Familiarity with pytorch for deep learning
- RESTful API development using fastapi
- Must have pytest experience for writing unit tests
"""

SAMPLE_JD_PREFERRED = """
Nice to have:
- Experience with docker containerization
- Knowledge of kubernetes for orchestration
"""

COMBINED_JD = SAMPLE_JD_REQUIRED + "\n" + SAMPLE_JD_PREFERRED

MINIMAL_JD = "We need a Python developer with numpy and pandas experience."


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def test_jd_too_short_returns_422(client):
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": "Too short",
    })
    assert response.status_code == 422


def test_jd_too_long_returns_422(client):
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": "x" * 10_001,
    })
    assert response.status_code == 422


def test_missing_job_description_returns_422(client):
    response = client.post("/api/v1/skillgraph/match", json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# No analysis_result (JD-only mode)
# ---------------------------------------------------------------------------

def test_match_without_analysis_result_returns_200(client):
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": MINIMAL_JD,
    })
    assert response.status_code == 200
    data = response.json()
    assert "skills_required" in data
    assert "skills_preferred" in data
    assert "summary" in data
    assert "disclaimer" in data


def test_match_without_analysis_all_tiers_none(client):
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": SAMPLE_JD_REQUIRED,
    })
    assert response.status_code == 200
    data = response.json()
    all_skills = data["skills_required"] + data["skills_preferred"]
    assert len(all_skills) > 0
    for skill in all_skills:
        assert skill["evidence_tier"] == "none", (
            f"{skill['canonical_name']} should be 'none' without analysis_result"
        )


def test_match_without_analysis_recommendations_provided(client):
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": MINIMAL_JD,
    })
    data = response.json()
    all_skills = data["skills_required"] + data["skills_preferred"]
    for skill in all_skills:
        assert skill["recommendation"] is not None, (
            f"{skill['canonical_name']} should have a recommendation when tier is 'none'"
        )


# ---------------------------------------------------------------------------
# With analysis_result from fixture repo (no package imports in fixture)
# ---------------------------------------------------------------------------

def test_match_with_analysis_result_returns_200(client):
    # First scan the fixture repo
    scan_resp = client.post("/api/v1/repomind/analyze", json={"repo_path": FIXTURE_ROOT})
    assert scan_resp.status_code == 200
    analysis = scan_resp.json()

    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": MINIMAL_JD,
        "analysis_result": analysis,
    })
    assert response.status_code == 200
    data = response.json()
    assert "skills_required" in data
    assert "summary" in data


def test_match_required_vs_preferred_split(client):
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": COMBINED_JD,
    })
    assert response.status_code == 200
    data = response.json()

    req_names = {s["canonical_name"] for s in data["skills_required"]}
    pref_names = {s["canonical_name"] for s in data["skills_preferred"]}

    # numpy and sklearn appear in the Requirements section → required
    assert "numpy" in req_names or "scikit-learn" in req_names
    # docker and kubernetes appear in Nice to have → preferred
    assert "docker" in pref_names or "kubernetes" in pref_names


def test_match_sklearn_alias_normalised(client):
    jd = "Proficiency with sklearn is required. We also use scikit-learn pipelines."
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": jd,
    })
    assert response.status_code == 200
    data = response.json()
    all_skills = data["skills_required"] + data["skills_preferred"]
    sk_results = [s for s in all_skills if s["canonical_name"] == "scikit-learn"]
    assert len(sk_results) == 1, "sklearn and scikit-learn should produce exactly one result"
    assert "sklearn" in sk_results[0]["aliases_matched"] or "scikit-learn" in sk_results[0]["aliases_matched"]


def test_import_alone_never_strong_via_api(client):
    """
    Supply an analysis_result that has numpy in imported_packages but no symbols.
    The tier must be WEAK, never STRONG.
    """
    scan_resp = client.post("/api/v1/repomind/analyze", json={"repo_path": FIXTURE_ROOT})
    assert scan_resp.status_code == 200
    analysis = scan_resp.json()

    # Inject numpy into imported_packages (fixture repo doesn't import numpy)
    analysis["imported_packages"] = ["numpy"]
    analysis["symbols"] = []  # clear all symbols
    analysis["edges"] = []
    analysis["unresolved_calls"] = []

    jd = "Strong numpy experience required."
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": jd,
        "analysis_result": analysis,
    })
    assert response.status_code == 200
    data = response.json()
    all_skills = data["skills_required"] + data["skills_preferred"]
    np_results = [s for s in all_skills if s["canonical_name"] == "numpy"]
    assert len(np_results) == 1
    assert np_results[0]["evidence_tier"] == "weak", (
        "Import alone must produce 'weak', not 'strong'"
    )


def test_evidence_item_has_real_file_path(client):
    """
    When symbols are present, evidence items must carry real file paths and line numbers.
    """
    scan_resp = client.post("/api/v1/repomind/analyze", json={"repo_path": FIXTURE_ROOT})
    assert scan_resp.status_code == 200
    analysis = scan_resp.json()

    # Add a fake import + symbol for scikit-learn to trigger strong evidence
    analysis["imported_packages"] = ["sklearn"]
    analysis["symbols"].append({
        "id": "func:ml_model.py::train_sklearn_classifier",
        "name": "train_sklearn_classifier",
        "symbol_type": "function",
        "location": {
            "file_path": "ml_model.py",
            "start_line": 15,
            "end_line": 45,
            "start_col": 0,
            "end_col": 0,
        },
        "parent_id": None,
        "docstring": "Train a classifier using scikit-learn.",
    })

    jd = "Must have sklearn (scikit-learn) experience for classification."
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": jd,
        "analysis_result": analysis,
    })
    assert response.status_code == 200
    data = response.json()
    all_skills = data["skills_required"] + data["skills_preferred"]
    sk = next((s for s in all_skills if s["canonical_name"] == "scikit-learn"), None)
    assert sk is not None
    assert sk["evidence_tier"] == "strong"

    # Verify evidence items carry real metadata
    symbol_items = [e for e in sk["evidence_items"] if e["kind"] in ("symbol", "docstring")]
    assert len(symbol_items) >= 1
    item = symbol_items[0]
    assert item["file_path"] is not None
    assert item["start_line"] is not None
    assert item["end_line"] is not None


def test_summary_counts_are_consistent(client):
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": COMBINED_JD,
    })
    assert response.status_code == 200
    data = response.json()
    summary = data["summary"]
    all_skills = data["skills_required"] + data["skills_preferred"]

    assert summary["required_count"] == len(data["skills_required"])
    assert summary["preferred_count"] == len(data["skills_preferred"])
    assert (
        summary["strong_evidence_count"]
        + summary["weak_evidence_count"]
        + summary["no_evidence_count"]
        == len(all_skills)
    )


def test_disclaimer_is_present(client):
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": MINIMAL_JD,
    })
    assert response.status_code == 200
    data = response.json()
    assert "disclaimer" in data
    assert len(data["disclaimer"]) > 20


def test_repomind_regression_health_still_works(client):
    """Regression: health endpoint must be unaffected by SkillGraph addition."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_repomind_regression_analyze_still_works(client):
    """Regression: RepoMind analyze endpoint must be unaffected."""
    response = client.post("/api/v1/repomind/analyze", json={"repo_path": FIXTURE_ROOT})
    assert response.status_code == 200
    data = response.json()
    assert data["files_scanned"] == 5
    assert data["symbols_count"] == 16
    assert data["edges_count"] == 7
    assert "imported_packages" in data  # new backward-compatible field present
    assert isinstance(data["imported_packages"], list)


def test_match_api_target_role_customizes_roadmap(client):
    """Test target_role query customizes roadmap task relevance."""
    jd = "Requirements:\n- PyTorch experience required for model training."
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": jd,
        "target_role": "genai_engineer",
    })
    assert response.status_code == 200
    data = response.json()
    pt = next((s for s in data["skills_required"] if s["canonical_name"] == "pytorch"), None)
    assert pt is not None
    assert pt["roadmap_task"] is not None
    assert "genai" in pt["roadmap_task"]["target_role_relevance"].lower() or "attention" in pt["roadmap_task"]["target_role_relevance"].lower() or "transformer" in pt["roadmap_task"]["target_role_relevance"].lower()
    assert len(pt["roadmap_task"]["resources"]) >= 1


def test_match_api_includes_related_skills_and_resources(client):
    """Verify related_skills array is populated in API response."""
    jd = "Requirements:\n- Experience with FastAPI and NumPy required."
    response = client.post("/api/v1/skillgraph/match", json={
        "job_description": jd,
        "target_role": "sde",
    })
    assert response.status_code == 200
    data = response.json()
    fastapi_skill = next((s for s in data["skills_required"] if s["canonical_name"] == "fastapi"), None)
    assert fastapi_skill is not None
    assert len(fastapi_skill["related_skills"]) > 0
    assert "pydantic" in fastapi_skill["related_skills"] or "docker" in fastapi_skill["related_skills"]


def test_match_api_returns_role_tailored_roadmap(client):
    """Verify role_roadmap in API response matches the selected career role."""
    jd = "Requirements:\n- Python and NumPy required."

    # 1. AI/ML Engineer
    res_aiml = client.post("/api/v1/skillgraph/match", json={
        "job_description": jd,
        "target_role": "aiml_engineer",
    })
    assert res_aiml.status_code == 200
    data_aiml = res_aiml.json()
    assert "role_roadmap" in data_aiml
    assert len(data_aiml["role_roadmap"]) == 4
    aiml_skills = [t["skill_name"] for t in data_aiml["role_roadmap"]]
    assert aiml_skills == ["numpy", "pandas", "scikit-learn", "model-evaluation"]

    # 2. Generative AI Engineer
    res_genai = client.post("/api/v1/skillgraph/match", json={
        "job_description": jd,
        "target_role": "genai_engineer",
    })
    assert res_genai.status_code == 200
    data_genai = res_genai.json()
    assert len(data_genai["role_roadmap"]) == 4
    genai_skills = [t["skill_name"] for t in data_genai["role_roadmap"]]
    assert genai_skills == ["llm-api", "embeddings", "langchain", "generative-ai"]

    # 3. SDE
    res_sde = client.post("/api/v1/skillgraph/match", json={
        "job_description": jd,
        "target_role": "sde",
    })
    assert res_sde.status_code == 200
    data_sde = res_sde.json()
    assert len(data_sde["role_roadmap"]) == 4
    sde_skills = [t["skill_name"] for t in data_sde["role_roadmap"]]
    assert sde_skills == ["git", "fastapi", "postgresql", "pytest"]

    # Verify role_relevance and objective are non-empty for all roles via API
    for r_data in (data_aiml, data_genai, data_sde):
        for task in r_data["role_roadmap"]:
            assert task.get("role_relevance") or task.get("target_role_relevance")
            assert task.get("objective") or task.get("description")
            relevance = task.get("role_relevance") or task.get("target_role_relevance")
            objective = task.get("objective") or task.get("description")
            assert len(relevance.strip()) >= 20
            assert len(objective.strip()) >= 20
