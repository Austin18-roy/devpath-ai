/**
 * Core transformation function: symbols & edges to React Flow data.
 * Pure ES module for zero-dependency testability.
 */
export function symbolsAndEdgesToGraph(
  symbols,
  edges,
  impactReport = null,
  selectedSymbolId = null
) {
  const directCallerIds = new Set(
    impactReport ? impactReport.direct_callers.map((s) => s.id) : []
  );
  const transitiveImpactIds = new Set(
    impactReport
      ? impactReport.transitive_impacted_symbols.map((s) => s.id)
      : []
  );
  const isImpactActive = impactReport !== null;
  const targetId = impactReport ? impactReport.target_symbol_id : null;

  // Group symbols by file for clean, non-overlapping columnar layout
  const fileGroups = new Map();
  for (const sym of symbols) {
    const file = sym.location.file_path;
    const group = fileGroups.get(file) || [];
    group.push(sym);
    fileGroups.set(file, group);
  }

  const nodes = [];
  let fileIndex = 0;

  for (const [, fileSymbols] of fileGroups.entries()) {
    const xPos = fileIndex * 340 + 40;

    fileSymbols.forEach((sym, symIndex) => {
      const yPos = symIndex * 130 + 40;

      const isTarget = sym.id === targetId;
      const isDirectCaller = directCallerIds.has(sym.id);
      const isTransitiveImpact = transitiveImpactIds.has(sym.id) && !isDirectCaller;
      const isSelected = sym.id === selectedSymbolId;

      const isAffected = isTarget || isDirectCaller || isTransitiveImpact;
      const isDimmed = isImpactActive && !isAffected;

      nodes.push({
        id: sym.id,
        type: "default",
        position: { x: xPos, y: yPos },
        data: {
          label: `${sym.name} (${sym.symbol_type})`,
          symbol: sym,
          isTarget,
          isDirectCaller,
          isTransitiveImpact,
          isDimmed,
          isSelected,
        },
        style: {
          width: 260,
          padding: 12,
          borderRadius: 12,
          fontSize: 12,
          background: isTarget
            ? "#ecfeff"
            : isDirectCaller
            ? "#fffbeb"
            : isTransitiveImpact
            ? "#fff1f2"
            : isSelected
            ? "#eff6ff"
            : "#ffffff",
          color: "#18181b",
          border: isTarget
            ? "2px solid #06b6d4"
            : isDirectCaller
            ? "2px solid #f59e0b"
            : isTransitiveImpact
            ? "2px solid #f43f5e"
            : isSelected
            ? "2px solid #3b82f6"
            : "1px solid #e4e4e7",
          opacity: isDimmed ? 0.35 : 1,
          boxShadow: isTarget || isDirectCaller || isTransitiveImpact
            ? "0 4px 14px rgba(0, 0, 0, 0.12)"
            : "0 1px 3px rgba(0, 0, 0, 0.05)",
          cursor: "pointer",
        },
      });
    });

    fileIndex++;
  }

  // Construct React Flow edges
  const symbolIdsSet = new Set(symbols.map((s) => s.id));
  const graphEdges = [];

  edges.forEach((edge, index) => {
    if (!symbolIdsSet.has(edge.source_id) || !symbolIdsSet.has(edge.target_id)) {
      return;
    }

    const isEdgeImpacted =
      isImpactActive &&
      (edge.target_id === targetId ||
        directCallerIds.has(edge.source_id) ||
        transitiveImpactIds.has(edge.source_id));

    graphEdges.push({
      id: `e-${index}-${edge.source_id}-${edge.target_id}`,
      source: edge.source_id,
      target: edge.target_id,
      label: edge.edge_type,
      animated: isEdgeImpacted,
      style: {
        stroke: isEdgeImpacted ? "#f59e0b" : "#94a3b8",
        strokeWidth: isEdgeImpacted ? 2.5 : 1.5,
        opacity: isImpactActive && !isEdgeImpacted ? 0.3 : 1,
      },
      markerEnd: {
        type: "arrowclosed",
        width: 14,
        height: 14,
        color: isEdgeImpacted ? "#f59e0b" : "#94a3b8",
      },
    });
  });

  return { nodes, edges: graphEdges };
}
