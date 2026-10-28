from pathlib import Path
from app.services.repomind.graph import RepoDependencyGraph
from app.services.repomind.parser import RepoMindParser

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "sample_repo"


def get_fixture_graph() -> RepoDependencyGraph:
    parser = RepoMindParser(repo_path=FIXTURE_ROOT)
    analysis = parser.parse_repository()
    return RepoDependencyGraph(analysis)


def test_graph_symbol_lookup():
    """Verify symbol lookup returns the expected CodeSymbol."""
    graph = get_fixture_graph()
    symbol = graph.get_symbol("func:math_utils.py::multiply")
    assert symbol is not None
    assert symbol.name == "multiply"


def test_graph_direct_dependencies():
    """Verify direct dependencies of square returns multiply (square -> multiply)."""
    graph = get_fixture_graph()
    deps = graph.get_dependencies("func:math_utils.py::square")
    dep_ids = [d.id for d in deps]
    assert "func:math_utils.py::multiply" in dep_ids


def test_graph_direct_callers():
    """Verify direct callers of multiply includes square and apply_tax."""
    graph = get_fixture_graph()
    callers = graph.get_callers("func:math_utils.py::multiply")
    caller_ids = [c.id for c in callers]
    assert "func:math_utils.py::square" in caller_ids
    assert "func:calculator.py::Calculator.apply_tax" in caller_ids


def test_graph_change_impact_reverse_reachability():
    """
    Verify change impact:
    Modifying math_utils.multiply affects:
    - Direct: square, Calculator.apply_tax
    - Transitive: Calculator.process_order (which calls apply_tax)
    - Upstream: pipeline.run_pipeline
    """
    graph = get_fixture_graph()
    report = graph.get_change_impact("func:math_utils.py::multiply")

    assert report.target_symbol_id == "func:math_utils.py::multiply"
    assert report.total_impacted_count >= 3

    direct_ids = [s.id for s in report.direct_callers]
    assert "func:math_utils.py::square" in direct_ids
    assert "func:calculator.py::Calculator.apply_tax" in direct_ids

    all_impacted_ids = [s.id for s in report.transitive_impacted_symbols]
    # Calculator.process_order calls apply_tax, so it must be transitively impacted
    assert "func:calculator.py::Calculator.process_order" in all_impacted_ids

    # Files affected must span across math_utils.py and calculator.py
    assert "math_utils.py" in report.impacted_files
    assert "calculator.py" in report.impacted_files


def test_graph_change_impact_unknown_symbol():
    """Verify requesting impact for an unknown symbol returns empty report gracefully."""
    graph = get_fixture_graph()
    report = graph.get_change_impact("func:nonexistent.py::missing")
    assert report.total_impacted_count == 0
    assert "not found" in report.explanation


def test_graph_to_dict_serialization():
    """Verify graph exports to a structured dictionary."""
    graph = get_fixture_graph()
    data = graph.to_dict()
    assert "node_count" in data
    assert "edge_count" in data
    assert data["node_count"] > 0
    assert data["edge_count"] > 0
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)

