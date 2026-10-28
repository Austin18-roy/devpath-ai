import { Edge, Node } from "@xyflow/react";
import {
  CodeSymbol,
  DependencyEdge,
  ChangeImpactReport,
} from "./repomind-types";
import { symbolsAndEdgesToGraph as coreTransform } from "./graph-adapter-core.mjs";

export interface SymbolNodeData {
  symbol: CodeSymbol;
  isTarget: boolean;
  isDirectCaller: boolean;
  isTransitiveImpact: boolean;
  isDimmed: boolean;
  isSelected: boolean;
  [key: string]: unknown;
}

export interface GraphAdapterOutput {
  nodes: Node<SymbolNodeData>[];
  edges: Edge[];
}

export function symbolsAndEdgesToGraph(
  symbols: CodeSymbol[],
  edges: DependencyEdge[],
  impactReport: ChangeImpactReport | null = null,
  selectedSymbolId: string | null = null
): GraphAdapterOutput {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (coreTransform as any)(
    symbols,
    edges,
    impactReport,
    selectedSymbolId
  ) as GraphAdapterOutput;
}
