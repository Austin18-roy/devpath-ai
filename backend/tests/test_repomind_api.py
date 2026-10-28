from pathlib import Path

FIXTURE_ROOT = str(Path(__file__).parent / "fixtures" / "sample_repo")


def test_api_analyze_repository(client):
    """Test POST /api/v1/repomind/analyze with absolute fixture path."""
    response = client.post("/api/v1/repomind/analyze", json={"repo_path": FIXTURE_ROOT})
    assert response.status_code == 200
    data = response.json()
    assert data["files_scanned"] >= 4
    assert data["symbols_count"] > 0
    assert data["edges_count"] > 0
    assert len(data["limitations"]) > 0


def test_api_analyze_relative_path_from_project_root(client):
    """Test POST /api/v1/repomind/analyze with 'backend/tests/fixtures/sample_repo'."""
    response = client.post(
        "/api/v1/repomind/analyze",
        json={"repo_path": "backend/tests/fixtures/sample_repo"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["files_scanned"] >= 4
    symbol_names = [s["name"] for s in data["symbols"]]
    assert "multiply" in symbol_names


def test_api_analyze_relative_path_from_backend_dir(client):
    """Test POST /api/v1/repomind/analyze with 'tests/fixtures/sample_repo'."""
    response = client.post(
        "/api/v1/repomind/analyze",
        json={"repo_path": "tests/fixtures/sample_repo"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["files_scanned"] >= 4
    symbol_names = [s["name"] for s in data["symbols"]]
    assert "multiply" in symbol_names


def test_api_analyze_multiply_impact_with_callers(client):
    """
    Test POST /api/v1/repomind/impact specifically on 'multiply'
    using the frontend's default relative path.
    """
    payload = {
        "repo_path": "backend/tests/fixtures/sample_repo",
        "symbol_id": "func:math_utils.py::multiply",
    }
    response = client.post("/api/v1/repomind/impact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_symbol_id"] == "func:math_utils.py::multiply"
    assert data["total_impacted_count"] == 3

    direct_caller_ids = [s["id"] for s in data["direct_callers"]]
    assert "func:calculator.py::Calculator.apply_tax" in direct_caller_ids
    assert "func:math_utils.py::square" in direct_caller_ids

    transitive_ids = [s["id"] for s in data["transitive_impacted_symbols"]]
    assert "func:calculator.py::Calculator.process_order" in transitive_ids


def test_api_analyze_zero_caller_impact(client):
    """Test POST /api/v1/repomind/impact on a symbol with zero callers (run_pipeline)."""
    payload = {
        "repo_path": "backend/tests/fixtures/sample_repo",
        "symbol_id": "func:pipeline.py::run_pipeline",
    }
    response = client.post("/api/v1/repomind/impact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_symbol_id"] == "func:pipeline.py::run_pipeline"
    assert data["total_impacted_count"] == 0
    assert len(data["direct_callers"]) == 0
    assert len(data["transitive_impacted_symbols"]) == 0


def test_api_rejects_unauthorized_path(client):
    """Test POST /api/v1/repomind/analyze rejects unauthorized directory."""
    response = client.post("/api/v1/repomind/analyze", json={"repo_path": "/etc"})
    assert response.status_code == 400
    detail = response.json().get("detail", "")
    assert "outside allowed repository roots" in detail or "Access denied" in detail
