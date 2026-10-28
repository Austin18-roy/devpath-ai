from pathlib import Path
from app.services.repomind.models import EdgeType, SymbolType
from app.services.repomind.parser import RepoMindParser

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "sample_repo"


def test_parser_extracts_symbols_and_line_ranges():
    """Verify symbol extraction with correct types, line ranges, and docstrings."""
    parser = RepoMindParser(repo_path=FIXTURE_ROOT)
    result = parser.parse_repository()

    assert result.files_scanned >= 4
    symbol_ids = {s.id: s for s in result.symbols}

    # Verify math_utils functions
    add_sym = symbol_ids.get("func:math_utils.py::add")
    assert add_sym is not None
    assert add_sym.symbol_type == SymbolType.FUNCTION
    assert add_sym.name == "add"
    assert add_sym.location.file_path == "math_utils.py"
    assert add_sym.location.start_line == 3
    assert add_sym.location.end_line == 5
    assert "Add two numbers" in (add_sym.docstring or "")

    # Verify Calculator class and methods
    calc_class = symbol_ids.get("class:calculator.py::Calculator")
    assert calc_class is not None
    assert calc_class.symbol_type == SymbolType.CLASS
    assert calc_class.name == "Calculator"

    method_sym = symbol_ids.get("func:calculator.py::Calculator.compute_sum")
    assert method_sym is not None
    assert method_sym.symbol_type == SymbolType.METHOD
    assert method_sym.parent_id == "class:calculator.py::Calculator"


def test_parser_resolves_dependency_edges():
    """Verify call edges and inheritance relationships."""
    parser = RepoMindParser(repo_path=FIXTURE_ROOT)
    result = parser.parse_repository()

    # Verify class inheritance edge
    inherits_edges = [
        e for e in result.edges
        if e.source_id == "class:calculator.py::Calculator"
        and e.target_id == "class:calculator.py::BaseEngine"
        and e.edge_type == EdgeType.INHERITS
    ]
    assert len(inherits_edges) == 1

    # Verify intra-file call: square -> multiply
    intra_calls = [
        e for e in result.edges
        if e.source_id == "func:math_utils.py::square"
        and e.target_id == "func:math_utils.py::multiply"
        and e.edge_type == EdgeType.CALLS
    ]
    assert len(intra_calls) == 1

    # Verify cross-file call: compute_sum -> add
    cross_calls = [
        e for e in result.edges
        if e.source_id == "func:calculator.py::Calculator.compute_sum"
        and e.target_id == "func:math_utils.py::add"
        and e.edge_type == EdgeType.CALLS
    ]
    assert len(cross_calls) == 1

    # Verify self.method() call: process_order -> apply_tax & compute_sum
    self_calls = [
        e for e in result.edges
        if e.source_id == "func:calculator.py::Calculator.process_order"
        and e.target_id in {
            "func:calculator.py::Calculator.apply_tax",
            "func:calculator.py::Calculator.compute_sum",
        }
    ]
    assert len(self_calls) == 2


def test_syntax_error_resilience():
    """Verify malformed.py produces a diagnostic error but does not abort scanning."""
    parser = RepoMindParser(repo_path=FIXTURE_ROOT)
    result = parser.parse_repository()

    malformed_diagnostics = [
        d for d in result.diagnostics if "malformed.py" in d.file_path
    ]
    assert len(malformed_diagnostics) >= 1
    diag = malformed_diagnostics[0]
    assert diag.level == "error"
    assert "Syntax error" in diag.message

    # Other files must still be parsed successfully
    assert any("math_utils.py" in s.id for s in result.symbols)
    assert any("calculator.py" in s.id for s in result.symbols)


def test_deterministic_output():
    """Verify scanning the same repository twice produces identical symbol and edge orders."""
    parser = RepoMindParser(repo_path=FIXTURE_ROOT)
    run1 = parser.parse_repository()
    run2 = parser.parse_repository()

    assert [s.id for s in run1.symbols] == [s.id for s in run2.symbols]
    assert [(e.source_id, e.target_id) for e in run1.edges] == [(e.source_id, e.target_id) for e in run2.edges]

