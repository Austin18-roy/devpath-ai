/**
 * RepoMind Domain TypeScript Definitions
 * Directly matching backend Pydantic models from app.services.repomind.models
 */

export type SymbolType = "module" | "class" | "function" | "method";

export type EdgeType = "calls" | "imports" | "inherits" | "defines";

export interface SymbolLocation {
  file_path: string;
  start_line: number;
  end_line: number;
  start_col: number;
  end_col: number;
}

export interface CodeSymbol {
  id: string;
  name: string;
  symbol_type: SymbolType;
  location: SymbolLocation;
  parent_id: string | null;
  docstring: string | null;
}

export interface DependencyEdge {
  source_id: string;
  target_id: string;
  edge_type: EdgeType;
  line_number: number;
}

export interface UnresolvedCall {
  caller_symbol_id: string;
  call_expression: string;
  line_number: number;
  reason: string;
}

export interface ScanDiagnostic {
  file_path: string;
  level: "warning" | "error";
  message: string;
  line_number: number | null;
}

export interface AnalysisResult {
  repo_path: string;
  files_scanned: number;
  symbols_count: number;
  edges_count: number;
  symbols: CodeSymbol[];
  edges: DependencyEdge[];
  unresolved_calls: UnresolvedCall[];
  diagnostics: ScanDiagnostic[];
  limitations: string[];
}

export interface ChangeImpactReport {
  target_symbol_id: string;
  direct_callers: CodeSymbol[];
  transitive_impacted_symbols: CodeSymbol[];
  impacted_files: string[];
  total_impacted_count: number;
  explanation: string;
}

export interface AnalyzeRequest {
  repo_path: string;
}

export interface ImpactRequest {
  repo_path: string;
  symbol_id: string;
}

