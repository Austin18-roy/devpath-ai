from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SymbolType(str, Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"


class EdgeType(str, Enum):
    CALLS = "calls"
    IMPORTS = "imports"
    INHERITS = "inherits"
    DEFINES = "defines"


class SymbolLocation(BaseModel):
    file_path: str = Field(..., description="Repository-relative path of the source file")
    start_line: int = Field(..., description="1-based starting line number")
    end_line: int = Field(..., description="1-based ending line number")
    start_col: int = Field(0, description="0-based starting column offset")
    end_col: int = Field(0, description="0-based ending column offset")


class CodeSymbol(BaseModel):
    id: str = Field(..., description="Stable, unique symbol identifier within the repository")
    name: str = Field(..., description="Symbol name")
    symbol_type: SymbolType = Field(..., description="Type of symbol (module, class, function, method)")
    location: SymbolLocation = Field(..., description="Location of the symbol in source code")
    parent_id: Optional[str] = Field(None, description="Enclosing symbol ID (e.g. class ID for a method)")
    docstring: Optional[str] = Field(None, description="Extracted docstring if present")


class DependencyEdge(BaseModel):
    source_id: str = Field(..., description="Origin node: Caller / Dependent")
    target_id: str = Field(..., description="Destination node: Callee / Dependency")
    edge_type: EdgeType = Field(EdgeType.CALLS, description="Type of dependency relationship")
    line_number: int = Field(..., description="1-based line number where dependency occurs")


class UnresolvedCall(BaseModel):
    caller_symbol_id: str = Field(..., description="Symbol containing the unresolved call")
    call_expression: str = Field(..., description="String expression of the unresolvable call")
    line_number: int = Field(..., description="1-based line number of the call")
    reason: str = Field(..., description="Why the call could not be statically resolved")


class ScanDiagnostic(BaseModel):
    file_path: str = Field(..., description="Repository-relative file path")
    level: str = Field("warning", description="Severity level: 'warning' or 'error'")
    message: str = Field(..., description="Diagnostic message")
    line_number: Optional[int] = Field(None, description="Line number where problem occurred")


class AnalysisResult(BaseModel):
    repo_path: str = Field(..., description="Analyzed repository root path")
    files_scanned: int = Field(..., description="Total number of Python files successfully scanned")
    symbols_count: int = Field(..., description="Total extracted symbols")
    edges_count: int = Field(..., description="Total extracted dependency edges")
    symbols: List[CodeSymbol] = Field(default_factory=list)
    edges: List[DependencyEdge] = Field(default_factory=list)
    unresolved_calls: List[UnresolvedCall] = Field(default_factory=list)
    diagnostics: List[ScanDiagnostic] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class ChangeImpactReport(BaseModel):
    target_symbol_id: str = Field(..., description="Symbol ID evaluated for change impact")
    direct_callers: List[CodeSymbol] = Field(default_factory=list, description="Symbols that directly call/depend on the target")
    transitive_impacted_symbols: List[CodeSymbol] = Field(default_factory=list, description="All symbols reachable via reverse dependency traversal")
    impacted_files: List[str] = Field(default_factory=list, description="List of source files containing impacted symbols")
    total_impacted_count: int = Field(..., description="Total count of all directly and transitively impacted symbols")
    explanation: str = Field(..., description="Human-readable explanation of the impact analysis")


class AnalyzeRequest(BaseModel):
    repo_path: str = Field(..., description="Path to repository directory to analyze")


class ImpactRequest(BaseModel):
    repo_path: str = Field(..., description="Path to repository directory to analyze")
    symbol_id: str = Field(..., description="Target symbol ID to assess change impact for")

