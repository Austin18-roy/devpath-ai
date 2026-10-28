"use client";

import { useState } from "react";
import { AnalysisResult } from "@/lib/repomind-types";

interface RepoScannerProps {
  onAnalyze: (path: string) => Promise<void>;
  isLoading: boolean;
  result: AnalysisResult | null;
  error: string | null;
}

export function RepoScanner({ onAnalyze, isLoading, result, error }: RepoScannerProps) {
  const [repoPath, setRepoPath] = useState("backend/tests/fixtures/sample_repo");
  const [activeTab, setActiveTab] = useState<"diagnostics" | "unresolved" | "limitations" | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (repoPath.trim()) {
      onAnalyze(repoPath.trim());
    }
  };

  const handleLoadSample = () => {
    const samplePath = "backend/tests/fixtures/sample_repo";
    setRepoPath(samplePath);
    onAnalyze(samplePath);
  };

  return (
    <div className="w-full rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
            RepoMind Code Scanner
          </h2>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            Statically inspects Python codebases via AST without executing repository code.
          </p>
        </div>
        <button
          type="button"
          onClick={handleLoadSample}
          disabled={isLoading}
          className="inline-flex items-center justify-center rounded-lg border border-indigo-200 bg-indigo-50/80 px-3 py-1.5 text-xs font-semibold text-indigo-700 transition hover:bg-indigo-100 disabled:opacity-50 dark:border-indigo-900/60 dark:bg-indigo-950/40 dark:text-indigo-300 dark:hover:bg-indigo-950"
        >
          Load Verified Sample Fixture
        </button>
      </div>

      {/* Path Input Form */}
      <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <input
            type="text"
            value={repoPath}
            onChange={(e) => setRepoPath(e.target.value)}
            placeholder="e.g. backend/tests/fixtures/sample_repo"
            disabled={isLoading}
            className="w-full rounded-xl border border-zinc-300 bg-zinc-50/50 px-4 py-2.5 font-mono text-sm text-zinc-900 placeholder-zinc-400 focus:border-indigo-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:opacity-50 dark:border-zinc-700 dark:bg-zinc-800/50 dark:text-zinc-100 dark:focus:border-indigo-400 dark:focus:bg-zinc-900"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !repoPath.trim()}
          className="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500 disabled:opacity-50 dark:bg-indigo-500 dark:hover:bg-indigo-400"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Scanning AST...
            </span>
          ) : (
            "Analyze Codebase"
          )}
        </button>
      </form>

      {/* Error Banner */}
      {error && (
        <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50/70 p-4 text-sm text-rose-800 dark:border-rose-900/60 dark:bg-rose-950/20 dark:text-rose-200">
          <div className="flex items-start gap-2.5">
            <span className="text-base">⚠️</span>
            <div className="flex-1">
              <p className="font-semibold">Scan Request Failed</p>
              <p className="mt-0.5 text-xs text-rose-700 dark:text-rose-300">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Metrics Summary Bar */}
      {result && (
        <div className="mt-6 border-t border-zinc-100 pt-5 dark:border-zinc-800/80">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-5">
            <div className="rounded-xl border border-zinc-100 bg-zinc-50/80 p-3 dark:border-zinc-800/60 dark:bg-zinc-800/20">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Files Scanned</span>
              <p className="mt-1 text-lg font-bold text-zinc-900 dark:text-zinc-100">
                {result.files_scanned}
              </p>
            </div>
            <div className="rounded-xl border border-zinc-100 bg-zinc-50/80 p-3 dark:border-zinc-800/60 dark:bg-zinc-800/20">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Symbols Discovered</span>
              <p className="mt-1 text-lg font-bold text-indigo-600 dark:text-indigo-400">
                {result.symbols_count}
              </p>
            </div>
            <div className="rounded-xl border border-zinc-100 bg-zinc-50/80 p-3 dark:border-zinc-800/60 dark:bg-zinc-800/20">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Dependency Edges</span>
              <p className="mt-1 text-lg font-bold text-emerald-600 dark:text-emerald-400">
                {result.edges_count}
              </p>
            </div>
            <div className="rounded-xl border border-zinc-100 bg-zinc-50/80 p-3 dark:border-zinc-800/60 dark:bg-zinc-800/20">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Unresolved Calls</span>
              <p className="mt-1 text-lg font-bold text-amber-600 dark:text-amber-400">
                {result.unresolved_calls.length}
              </p>
            </div>
            <div className="rounded-xl border border-zinc-100 bg-zinc-50/80 p-3 dark:border-zinc-800/60 dark:bg-zinc-800/20">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Diagnostics</span>
              <p className={`mt-1 text-lg font-bold ${result.diagnostics.length > 0 ? "text-rose-600 dark:text-rose-400" : "text-zinc-700 dark:text-zinc-300"}`}>
                {result.diagnostics.length}
              </p>
            </div>
          </div>

          {/* Inspection Tabs */}
          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            <button
              onClick={() => setActiveTab(activeTab === "diagnostics" ? null : "diagnostics")}
              className={`rounded-lg px-3 py-1.5 font-medium transition ${
                activeTab === "diagnostics"
                  ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                  : "bg-zinc-100 text-zinc-700 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300"
              }`}
            >
              Diagnostics ({result.diagnostics.length})
            </button>
            <button
              onClick={() => setActiveTab(activeTab === "unresolved" ? null : "unresolved")}
              className={`rounded-lg px-3 py-1.5 font-medium transition ${
                activeTab === "unresolved"
                  ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                  : "bg-zinc-100 text-zinc-700 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300"
              }`}
            >
              Unresolved Calls ({result.unresolved_calls.length})
            </button>
            <button
              onClick={() => setActiveTab(activeTab === "limitations" ? null : "limitations")}
              className={`rounded-lg px-3 py-1.5 font-medium transition ${
                activeTab === "limitations"
                  ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                  : "bg-zinc-100 text-zinc-700 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300"
              }`}
            >
              Analysis Boundaries ({result.limitations.length})
            </button>
          </div>

          {/* Active Tab Panel */}
          {activeTab === "diagnostics" && (
            <div className="mt-3 max-h-56 overflow-y-auto rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-xs dark:border-zinc-800 dark:bg-zinc-950">
              {result.diagnostics.length === 0 ? (
                <p className="text-zinc-500">No syntax errors or scan warnings detected.</p>
              ) : (
                <div className="space-y-2">
                  {result.diagnostics.map((diag, i) => (
                    <div key={i} className="flex items-start gap-2 rounded-lg bg-white p-2 shadow-sm dark:bg-zinc-900">
                      <span className={`rounded px-1.5 py-0.5 font-bold uppercase text-[10px] ${diag.level === "error" ? "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300" : "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300"}`}>
                        {diag.level}
                      </span>
                      <div className="flex-1">
                        <p className="font-mono font-medium text-zinc-900 dark:text-zinc-100">
                          {diag.file_path} {diag.line_number ? `(Line ${diag.line_number})` : ""}
                        </p>
                        <p className="text-zinc-600 dark:text-zinc-400">{diag.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "unresolved" && (
            <div className="mt-3 max-h-56 overflow-y-auto rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-xs dark:border-zinc-800 dark:bg-zinc-950">
              {result.unresolved_calls.length === 0 ? (
                <p className="text-zinc-500">All calls were statically resolved within project scope.</p>
              ) : (
                <div className="space-y-2">
                  {result.unresolved_calls.map((call, i) => (
                    <div key={i} className="rounded-lg bg-white p-2.5 shadow-sm dark:bg-zinc-900">
                      <div className="flex items-center justify-between font-mono font-medium text-zinc-800 dark:text-zinc-200">
                        <span className="truncate">{call.call_expression}</span>
                        <span className="text-zinc-400">Line {call.line_number}</span>
                      </div>
                      <p className="mt-1 text-[11px] text-zinc-500 dark:text-zinc-400">
                        Caller: <code className="font-mono">{call.caller_symbol_id}</code>
                      </p>
                      <p className="mt-0.5 text-[11px] text-amber-700 dark:text-amber-300">
                        Reason: {call.reason}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "limitations" && (
            <div className="mt-3 rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-xs dark:border-zinc-800 dark:bg-zinc-950">
              <p className="font-semibold text-zinc-800 dark:text-zinc-200">
                Documented Python Static Analysis Boundaries:
              </p>
              <ul className="mt-2 list-inside list-disc space-y-1 text-zinc-600 dark:text-zinc-400">
                {result.limitations.map((lim, i) => (
                  <li key={i}>{lim}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

