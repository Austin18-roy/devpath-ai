"use client";

import { CodeSymbol, DependencyEdge, ChangeImpactReport } from "@/lib/repomind-types";

interface SymbolDetailsDrawerProps {
  symbol: CodeSymbol | null;
  edges: DependencyEdge[];
  allSymbols: CodeSymbol[];
  onAnalyzeImpact: (symbolId: string) => Promise<void>;
  isAnalyzingImpact: boolean;
  impactReport: ChangeImpactReport | null;
  impactError: string | null;
  onClearImpact: () => void;
  onSelectSymbolById: (symbolId: string) => void;
}

export function SymbolDetailsDrawer({
  symbol,
  edges,
  allSymbols,
  onAnalyzeImpact,
  isAnalyzingImpact,
  impactReport,
  impactError,
  onClearImpact,
  onSelectSymbolById,
}: SymbolDetailsDrawerProps) {
  if (!symbol) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-2xl border border-zinc-200 bg-white p-6 text-center shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="rounded-xl bg-zinc-100 p-3 text-zinc-400 dark:bg-zinc-800">
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
          </svg>
        </div>
        <h3 className="mt-3 text-sm font-semibold text-zinc-900 dark:text-zinc-100">
          No Symbol Selected
        </h3>
        <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
          Click any symbol node on the graph canvas to inspect its source location, dependencies, and evaluate potential change impact.
        </p>
      </div>
    );
  }

  // Find direct callers (incoming edges: source -> symbol.id)
  const incomingEdges = edges.filter((e) => e.target_id === symbol.id);
  // Find direct dependencies (outgoing edges: symbol.id -> target)
  const outgoingEdges = edges.filter((e) => e.source_id === symbol.id);

  const symbolMap = new Map(allSymbols.map((s) => [s.id, s]));

  const typeBadgeColors: Record<string, string> = {
    function: "bg-purple-100 text-purple-700 dark:bg-purple-950/70 dark:text-purple-300",
    method: "bg-indigo-100 text-indigo-700 dark:bg-indigo-950/70 dark:text-indigo-300",
    class: "bg-blue-100 text-blue-700 dark:bg-blue-950/70 dark:text-blue-300",
    module: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/70 dark:text-emerald-300",
  };

  const isCurrentSymbolImpacted = impactReport?.target_symbol_id === symbol.id;

  return (
    <div className="flex h-full flex-col justify-between overflow-y-auto rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="space-y-5">
        {/* Header */}
        <div>
          <div className="flex items-center gap-2">
            <span
              className={`rounded-md px-2 py-0.5 text-[11px] font-bold uppercase tracking-wider ${
                typeBadgeColors[symbol.symbol_type] || "bg-zinc-100 text-zinc-700"
              }`}
            >
              {symbol.symbol_type}
            </span>
            <span className="font-mono text-xs text-zinc-400">
              Lines {symbol.location.start_line} - {symbol.location.end_line}
            </span>
          </div>

          <h3 className="mt-2 text-xl font-bold text-zinc-900 break-words dark:text-zinc-50">
            {symbol.name}
          </h3>

          <p className="mt-1 font-mono text-xs text-zinc-500 break-all dark:text-zinc-400">
            {symbol.id}
          </p>
        </div>

        {/* Source Location */}
        <div className="rounded-xl border border-zinc-100 bg-zinc-50 p-3 text-xs dark:border-zinc-800/60 dark:bg-zinc-800/40">
          <span className="font-medium text-zinc-500 dark:text-zinc-400">Source File:</span>
          <p className="mt-0.5 font-mono font-medium text-zinc-800 dark:text-zinc-200">
            {symbol.location.file_path}
          </p>
          {symbol.parent_id && (
            <p className="mt-1 text-[11px] text-zinc-500 dark:text-zinc-400">
              Parent: <code className="font-mono">{symbol.parent_id}</code>
            </p>
          )}
          {symbol.docstring && (
            <div className="mt-2 border-t border-zinc-200/60 pt-2 text-zinc-600 italic dark:border-zinc-700/60 dark:text-zinc-300">
              &quot;{symbol.docstring}&quot;
            </div>
          )}
        </div>

        {/* Action: Evaluate Change Impact */}
        <div className="pt-1">
          <button
            type="button"
            onClick={() => onAnalyzeImpact(symbol.id)}
            disabled={isAnalyzingImpact}
            className="w-full inline-flex items-center justify-center rounded-xl bg-amber-500 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-amber-400 disabled:opacity-50 dark:bg-amber-600 dark:hover:bg-amber-500"
          >
            {isAnalyzingImpact ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Evaluating Reverse Reachability...
              </span>
            ) : (
              `Analyze Change Impact (${symbol.name})`
            )}
          </button>
        </div>

        {/* Visible Error Banner if Impact Request Fails */}
        {impactError && (
          <div className="rounded-xl border border-rose-200 bg-rose-50/80 p-3 text-xs text-rose-800 dark:border-rose-900/60 dark:bg-rose-950/20 dark:text-rose-200">
            <div className="flex items-start gap-2">
              <span className="text-base">⚠️</span>
              <div className="flex-1">
                <p className="font-semibold">Impact Evaluation Failed</p>
                <p className="mt-0.5 text-rose-700 dark:text-rose-300">{impactError}</p>
              </div>
            </div>
          </div>
        )}

        {/* Change Impact Report Section */}
        {impactReport && isCurrentSymbolImpacted && (
          <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-4 text-xs dark:border-amber-900/60 dark:bg-amber-950/20">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-amber-900 dark:text-amber-200">
                Potential Change Impact Report
              </span>
              <button
                onClick={onClearImpact}
                className="text-[11px] font-medium text-amber-700 underline hover:text-amber-900 dark:text-amber-300"
              >
                Clear Highlights
              </button>
            </div>

            <p className="mt-2 text-zinc-700 dark:text-zinc-300">
              {impactReport.explanation}
            </p>

            {impactReport.total_impacted_count === 0 ? (
              <div className="mt-3 rounded-lg bg-emerald-50 p-2.5 text-emerald-800 border border-emerald-200/60 dark:bg-emerald-950/30 dark:text-emerald-300 dark:border-emerald-900/40">
                <p className="font-medium">No upstream callers detected.</p>
                <p className="mt-0.5 text-[11px] text-emerald-700 dark:text-emerald-400">
                  Modifying this symbol has zero potential callers in this repository (leaf or entry-point symbol).
                </p>
              </div>
            ) : (
              <div className="mt-3 space-y-2">
                <div>
                  <span className="font-semibold text-amber-800 dark:text-amber-300">
                    Direct Callers ({impactReport.direct_callers.length}):
                  </span>
                  {impactReport.direct_callers.length === 0 ? (
                    <p className="text-zinc-500 italic mt-0.5">None (no direct calls detected)</p>
                  ) : (
                    <ul className="mt-1 space-y-1">
                      {impactReport.direct_callers.map((dc) => (
                        <li key={dc.id}>
                          <button
                            onClick={() => onSelectSymbolById(dc.id)}
                            className="font-mono text-[11px] text-amber-700 hover:underline dark:text-amber-300"
                          >
                            • {dc.name} ({dc.location.file_path})
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div>
                  <span className="font-semibold text-rose-800 dark:text-rose-300">
                    Transitive Impacted Callers ({impactReport.transitive_impacted_symbols.length}):
                  </span>
                  <ul className="mt-1 space-y-1">
                    {impactReport.transitive_impacted_symbols.map((tc) => (
                      <li key={tc.id}>
                        <button
                          onClick={() => onSelectSymbolById(tc.id)}
                          className="font-mono text-[11px] text-rose-700 hover:underline dark:text-rose-300"
                        >
                          • {tc.name} ({tc.location.file_path})
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <span className="font-semibold text-zinc-700 dark:text-zinc-300">
                    Affected Files ({impactReport.impacted_files.length}):
                  </span>
                  <p className="font-mono text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5">
                    {impactReport.impacted_files.join(", ")}
                  </p>
                </div>
              </div>
            )}

            <p className="mt-3 text-[10px] text-amber-800/80 dark:text-amber-300/80 italic border-t border-amber-200/60 pt-2">
              Note: Static analysis reports potential caller dependencies. It indicates affected upstream paths, not guaranteed runtime failure.
            </p>
          </div>
        )}

        {/* Direct Dependencies */}
        <div className="space-y-3">
          <div>
            <h4 className="text-xs font-semibold text-zinc-800 dark:text-zinc-200">
              Direct Dependencies (Calls {outgoingEdges.length}):
            </h4>
            {outgoingEdges.length === 0 ? (
              <p className="text-xs text-zinc-400 italic mt-1">No downstream calls detected.</p>
            ) : (
              <ul className="mt-1.5 space-y-1 text-xs">
                {outgoingEdges.map((e, idx) => {
                  const targetSym = symbolMap.get(e.target_id);
                  return (
                    <li key={idx} className="flex items-center justify-between font-mono text-[11px]">
                      <button
                        onClick={() => onSelectSymbolById(e.target_id)}
                        className="text-indigo-600 hover:underline dark:text-indigo-400 truncate max-w-[200px]"
                      >
                        {targetSym ? targetSym.name : e.target_id}
                      </button>
                      <span className="text-zinc-400 text-[10px]">L{e.line_number}</span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <div>
            <h4 className="text-xs font-semibold text-zinc-800 dark:text-zinc-200">
              Direct Callers (Called by {incomingEdges.length}):
            </h4>
            {incomingEdges.length === 0 ? (
              <p className="text-xs text-zinc-400 italic mt-1">No direct callers within scanned scope.</p>
            ) : (
              <ul className="mt-1.5 space-y-1 text-xs">
                {incomingEdges.map((e, idx) => {
                  const sourceSym = symbolMap.get(e.source_id);
                  return (
                    <li key={idx} className="flex items-center justify-between font-mono text-[11px]">
                      <button
                        onClick={() => onSelectSymbolById(e.source_id)}
                        className="text-amber-600 hover:underline dark:text-amber-400 truncate max-w-[200px]"
                      >
                        {sourceSym ? sourceSym.name : e.source_id}
                      </button>
                      <span className="text-zinc-400 text-[10px]">L{e.line_number}</span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
