"use client";

import { useMemo } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  Node,
  Edge,
  NodeMouseHandler,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { CodeSymbol } from "@/lib/repomind-types";
import { SymbolNodeData } from "@/lib/graph-adapter";

interface RepoMindGraphViewProps {
  nodes: Node<SymbolNodeData>[];
  edges: Edge[];
  isLoading: boolean;
  onSelectSymbol: (symbol: CodeSymbol) => void;
  selectedSymbolId: string | null;
}

export function RepoMindGraphView({
  nodes,
  edges,
  isLoading,
  onSelectSymbol,
  selectedSymbolId,
}: RepoMindGraphViewProps) {
  const handleNodeClick: NodeMouseHandler<Node<SymbolNodeData>> = (
    _event,
    node
  ) => {
    if (node.data && node.data.symbol) {
      onSelectSymbol(node.data.symbol);
    }
  };

  const isLargeGraph = nodes.length > 50;

  // Legend items explaining node coloring
  const legend = useMemo(
    () => (
      <div className="absolute bottom-4 left-4 z-10 flex flex-wrap items-center gap-3 rounded-xl border border-zinc-200/80 bg-white/95 px-3 py-2 text-xs shadow-md backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/95">
        <span className="font-semibold text-zinc-700 dark:text-zinc-300">Legend:</span>
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full border border-zinc-300 bg-white dark:bg-zinc-800" />
          <span className="text-zinc-600 dark:text-zinc-400">Normal</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full border-2 border-cyan-500 bg-cyan-100" />
          <span className="font-medium text-cyan-800 dark:text-cyan-300">Target</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full border-2 border-amber-500 bg-amber-100" />
          <span className="font-medium text-amber-800 dark:text-amber-300">Direct Caller</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full border-2 border-rose-500 bg-rose-100" />
          <span className="font-medium text-rose-800 dark:text-rose-300">Transitive Impact</span>
        </span>
      </div>
    ),
    []
  );

  return (
    <div className="relative h-[620px] w-full overflow-hidden rounded-2xl border border-zinc-200 bg-zinc-50 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-white/80 backdrop-blur-sm dark:bg-zinc-950/80">
          <div className="h-9 w-9 animate-spin rounded-full border-3 border-indigo-600 border-t-transparent" />
          <p className="mt-3 text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Rendering dependency graph...
          </p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && nodes.length === 0 && (
        <div className="flex h-full flex-col items-center justify-center p-8 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-100 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-500">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 className="mt-4 text-base font-semibold text-zinc-900 dark:text-zinc-100">
            No Dependency Graph Loaded
          </h3>
          <p className="mt-1 max-w-sm text-xs text-zinc-500 dark:text-zinc-400">
            Enter a Python repository path above and click &quot;Analyze Codebase&quot; to inspect symbols and call relationships.
          </p>
        </div>
      )}

      {/* Large Graph Banner */}
      {isLargeGraph && (
        <div className="absolute top-4 left-4 z-10 rounded-lg bg-amber-50 px-3 py-1 text-xs text-amber-800 shadow-sm border border-amber-200 dark:bg-amber-950/70 dark:text-amber-200 dark:border-amber-900">
          Large repository ({nodes.length} symbols). Use scroll wheel to zoom or click Minimap to navigate.
        </div>
      )}

      {/* Selected Symbol Indicator Banner */}
      {selectedSymbolId && (
        <div className="absolute top-4 right-4 z-10 rounded-lg bg-white/90 px-3 py-1 text-xs font-mono text-zinc-700 shadow-sm border border-zinc-200 backdrop-blur dark:bg-zinc-900/90 dark:text-zinc-300 dark:border-zinc-800">
          Selected: <span className="text-indigo-600 dark:text-indigo-400 font-medium">{selectedSymbolId}</span>
        </div>
      )}

      {/* React Flow Canvas */}
      {nodes.length > 0 && (
        <>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodeClick={handleNodeClick}
            fitView
            minZoom={0.2}
            maxZoom={1.8}
            attributionPosition="bottom-right"
          >
            <Background gap={18} size={1} color="#cbd5e1" />
            <Controls className="!bg-white !border-zinc-200 !shadow-sm dark:!bg-zinc-900 dark:!border-zinc-850" />
            <MiniMap
              nodeColor={(n) => {
                if (n.data?.isTarget) return "#06b6d4";
                if (n.data?.isDirectCaller) return "#f59e0b";
                if (n.data?.isTransitiveImpact) return "#f43f5e";
                return "#94a3b8";
              }}
              className="!border-zinc-200 !bg-white/90 dark:!border-zinc-800 dark:!bg-zinc-900/90"
              maskColor="rgba(240, 240, 240, 0.6)"
            />
          </ReactFlow>
          {legend}
        </>
      )}
    </div>
  );
}
