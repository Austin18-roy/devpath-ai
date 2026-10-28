from typing import Dict, List, Optional, Set
import networkx as nx

from app.services.repomind.models import (
    AnalysisResult,
    ChangeImpactReport,
    CodeSymbol,
    DependencyEdge,
    SymbolLocation,
    SymbolType,
)


class RepoDependencyGraph:
    """
    NetworkX-backed directed dependency graph for repository code symbols.
    
    GRAPH EDGE CONVENTION:
        Directed edge: Caller / Dependent  --->  Callee / Dependency
        Example:
            func:orders.py::checkout  --->  func:tax.py::calc_tax
            (checkout depends on and calls calc_tax)
            
    TRAVERSAL RULES:
        - Direct Dependencies of X: G.successors(X) (What does X call?)
        - Direct Callers of X:       G.predecessors(X) (Who calls X?)
        - Change Impact of X:        nx.ancestors(G, X) (All upstream callers affected by changes to X)
    """

    def __init__(self, analysis_result: Optional[AnalysisResult] = None):
        self.graph = nx.DiGraph()
        self.symbols_map: Dict[str, CodeSymbol] = {}
        
        if analysis_result:
            self.load_analysis(analysis_result)

    def load_analysis(self, analysis_result: AnalysisResult) -> None:
        """Populate the graph from an AnalysisResult."""
        for sym in analysis_result.symbols:
            self.add_symbol(sym)

        for edge in analysis_result.edges:
            self.add_edge(edge)

    def add_symbol(self, symbol: CodeSymbol) -> None:
        """Add a CodeSymbol node to the graph."""
        self.symbols_map[symbol.id] = symbol
        self.graph.add_node(
            symbol.id,
            name=symbol.name,
            symbol_type=symbol.symbol_type.value,
            file_path=symbol.location.file_path,
            start_line=symbol.location.start_line,
            end_line=symbol.location.end_line,
            start_col=symbol.location.start_col,
            end_col=symbol.location.end_col,
            parent_id=symbol.parent_id,
            docstring=symbol.docstring,
        )

    def add_edge(self, edge: DependencyEdge) -> None:
        """
        Add a directed dependency edge.
        Convention: edge.source_id (caller) ---> edge.target_id (callee)
        """
        self.graph.add_edge(
            edge.source_id,
            edge.target_id,
            edge_type=edge.edge_type.value,
            line_number=edge.line_number,
        )

    def get_symbol(self, symbol_id: str) -> Optional[CodeSymbol]:
        """Look up a CodeSymbol by its unique ID."""
        return self.symbols_map.get(symbol_id)

    def get_dependencies(self, symbol_id: str) -> List[CodeSymbol]:
        """
        Return direct dependencies called or used by symbol_id.
        Traverses G.successors(symbol_id).
        """
        if symbol_id not in self.graph:
            return []
        callee_ids = sorted(self.graph.successors(symbol_id))
        return [self.symbols_map[cid] for cid in callee_ids if cid in self.symbols_map]

    def get_callers(self, symbol_id: str) -> List[CodeSymbol]:
        """
        Return direct callers that depend on or call symbol_id.
        Traverses G.predecessors(symbol_id).
        """
        if symbol_id not in self.graph:
            return []
        caller_ids = sorted(self.graph.predecessors(symbol_id))
        return [self.symbols_map[cid] for cid in caller_ids if cid in self.symbols_map]

    def get_change_impact(self, symbol_id: str) -> ChangeImpactReport:
        """
        Compute change impact using reverse-reachability on the directed graph.
        
        Because edges point from caller to callee (caller ---> callee),
        any node that can reach symbol_id is an upstream dependent that may break
        if symbol_id changes. In NetworkX, this is exactly nx.ancestors(G, symbol_id).
        """
        if symbol_id not in self.graph:
            return ChangeImpactReport(
                target_symbol_id=symbol_id,
                direct_callers=[],
                transitive_impacted_symbols=[],
                impacted_files=[],
                total_impacted_count=0,
                explanation=f"Symbol '{symbol_id}' was not found in the repository graph.",
            )

        # Direct callers (immediate predecessors)
        direct_caller_ids = set(self.graph.predecessors(symbol_id))
        direct_callers = [
            self.symbols_map[cid] for cid in sorted(direct_caller_ids) if cid in self.symbols_map
        ]

        # Reverse reachability: all ancestors in the directed call graph
        all_impacted_ids = nx.ancestors(self.graph, symbol_id)

        # Sort impacted symbols by distance to target (nearest callers first)
        # We compute shortest path distance in the reversed graph (target -> caller)
        rev_graph = self.graph.reverse(copy=False)
        distance_map: Dict[str, int] = {}
        for imp_id in all_impacted_ids:
            try:
                distance_map[imp_id] = nx.shortest_path_length(rev_graph, symbol_id, imp_id)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                distance_map[imp_id] = 9999

        sorted_impacted_ids = sorted(
            all_impacted_ids,
            key=lambda nid: (distance_map.get(nid, 9999), nid)
        )

        impacted_symbols = [
            self.symbols_map[sid] for sid in sorted_impacted_ids if sid in self.symbols_map
        ]

        # Extract affected files
        impacted_files_set: Set[str] = set()
        for sym in impacted_symbols:
            impacted_files_set.add(sym.location.file_path)

        # Also add target symbol's own file
        if symbol_id in self.symbols_map:
            impacted_files_set.add(self.symbols_map[symbol_id].location.file_path)

        sorted_files = sorted(impacted_files_set)
        total_count = len(impacted_symbols)

        explanation = (
            f"Modifying '{symbol_id}' directly affects {len(direct_callers)} caller(s) "
            f"and transitively impacts {total_count} upstream symbol(s) across {len(sorted_files)} file(s)."
        )

        return ChangeImpactReport(
            target_symbol_id=symbol_id,
            direct_callers=direct_callers,
            transitive_impacted_symbols=impacted_symbols,
            impacted_files=sorted_files,
            total_impacted_count=total_count,
            explanation=explanation,
        )

    def to_dict(self) -> dict:
        """Produce a structured, JSON-serializable dictionary representation of the graph."""
        nodes_data = []
        for node_id, data in self.graph.nodes(data=True):
            nodes_data.append({"id": node_id, **data})

        edges_data = []
        for src, dst, data in self.graph.edges(data=True):
            edges_data.append({"source": src, "target": dst, **data})

        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "nodes": sorted(nodes_data, key=lambda n: n["id"]),
            "edges": sorted(edges_data, key=lambda e: (e["source"], e["target"])),
        }

