import test from "node:test";
import assert from "node:assert/strict";
import { symbolsAndEdgesToGraph } from "../src/lib/graph-adapter-core.mjs";

const sampleSymbols = [
  {
    id: "func:math_utils.py::multiply",
    name: "multiply",
    symbol_type: "function",
    location: { file_path: "math_utils.py", start_line: 8, end_line: 10, start_col: 0, end_col: 20 },
    parent_id: "module:math_utils.py",
    docstring: "Multiply numbers",
  },
  {
    id: "func:math_utils.py::square",
    name: "square",
    symbol_type: "function",
    location: { file_path: "math_utils.py", start_line: 13, end_line: 15, start_col: 0, end_col: 25 },
    parent_id: "module:math_utils.py",
    docstring: "Square numbers",
  },
  {
    id: "func:calculator.py::Calculator.apply_tax",
    name: "apply_tax",
    symbol_type: "method",
    location: { file_path: "calculator.py", start_line: 18, end_line: 20, start_col: 4, end_col: 37 },
    parent_id: "class:calculator.py::Calculator",
    docstring: "Apply tax",
  },
  {
    id: "func:pipeline.py::run_pipeline",
    name: "run_pipeline",
    symbol_type: "function",
    location: { file_path: "pipeline.py", start_line: 5, end_line: 8, start_col: 0, end_col: 40 },
    parent_id: "module:pipeline.py",
    docstring: "Run pipeline",
  },
];

const sampleEdges = [
  {
    source_id: "func:math_utils.py::square",
    target_id: "func:math_utils.py::multiply",
    edge_type: "calls",
    line_number: 14,
  },
  {
    source_id: "func:calculator.py::Calculator.apply_tax",
    target_id: "func:math_utils.py::multiply",
    edge_type: "calls",
    line_number: 19,
  },
];

test("symbolsAndEdgesToGraph creates nodes and preserves caller -> callee edge direction", () => {
  const { nodes, edges } = symbolsAndEdgesToGraph(sampleSymbols, sampleEdges, null, null);
  assert.equal(nodes.length, 4);
  assert.equal(edges.length, 2);

  // Check first edge: square (caller/source) -> multiply (callee/target)
  const edge1 = edges.find((e) => e.source === "func:math_utils.py::square");
  assert.ok(edge1);
  assert.equal(edge1.target, "func:math_utils.py::multiply");
  assert.equal(edge1.label, "calls");
});

test("symbolsAndEdgesToGraph without impact report does not dim nodes", () => {
  const { nodes } = symbolsAndEdgesToGraph(sampleSymbols, sampleEdges, null, null);
  for (const node of nodes) {
    assert.equal(node.data.isDimmed, false);
    assert.equal(node.data.isTarget, false);
    assert.equal(node.data.isDirectCaller, false);
  }
});

test("symbolsAndEdgesToGraph highlights target and distinguishes direct vs transitive impact", () => {
  const mockImpactReport = {
    target_symbol_id: "func:math_utils.py::multiply",
    direct_callers: [sampleSymbols[1]], // square
    transitive_impacted_symbols: [sampleSymbols[1], sampleSymbols[2]], // square, apply_tax
    impacted_files: ["math_utils.py", "calculator.py"],
    total_impacted_count: 2,
    explanation: "Potential impact detected",
  };

  const { nodes, edges } = symbolsAndEdgesToGraph(
    sampleSymbols,
    sampleEdges,
    mockImpactReport,
    "func:math_utils.py::multiply"
  );

  const targetNode = nodes.find((n) => n.id === "func:math_utils.py::multiply");
  assert.ok(targetNode);
  assert.equal(targetNode.data.isTarget, true);
  assert.equal(targetNode.data.isDimmed, false);

  const directCallerNode = nodes.find((n) => n.id === "func:math_utils.py::square");
  assert.ok(directCallerNode);
  assert.equal(directCallerNode.data.isDirectCaller, true);
  assert.equal(directCallerNode.data.isDimmed, false);

  const transitiveNode = nodes.find((n) => n.id === "func:calculator.py::Calculator.apply_tax");
  assert.ok(transitiveNode);
  assert.equal(transitiveNode.data.isTransitiveImpact, true);
  assert.equal(transitiveNode.data.isDimmed, false);

  // Unaffected node should be dimmed
  const unrelatedNode = nodes.find((n) => n.id === "func:pipeline.py::run_pipeline");
  assert.ok(unrelatedNode);
  assert.equal(unrelatedNode.data.isDimmed, true);

  // Edges leading to target should be animated
  for (const edge of edges) {
    assert.equal(edge.animated, true);
  }
});

test("symbolsAndEdgesToGraph handles zero-caller impact scenario cleanly", () => {
  const zeroCallerReport = {
    target_symbol_id: "func:pipeline.py::run_pipeline",
    direct_callers: [],
    transitive_impacted_symbols: [],
    impacted_files: ["pipeline.py"],
    total_impacted_count: 0,
    explanation: "Modifying 'run_pipeline' directly affects 0 callers.",
  };

  const { nodes, edges } = symbolsAndEdgesToGraph(
    sampleSymbols,
    sampleEdges,
    zeroCallerReport,
    "func:pipeline.py::run_pipeline"
  );

  // Target node should be marked as target and NOT dimmed
  const targetNode = nodes.find((n) => n.id === "func:pipeline.py::run_pipeline");
  assert.ok(targetNode);
  assert.equal(targetNode.data.isTarget, true);
  assert.equal(targetNode.data.isDimmed, false);

  // All other nodes should be dimmed because there are 0 callers
  const otherNodes = nodes.filter((n) => n.id !== "func:pipeline.py::run_pipeline");
  assert.equal(otherNodes.length, 3);
  for (const node of otherNodes) {
    assert.equal(node.data.isDimmed, true);
    assert.equal(node.data.isDirectCaller, false);
    assert.equal(node.data.isTransitiveImpact, false);
  }

  // No edges should be animated since none lead to target
  for (const edge of edges) {
    assert.equal(edge.animated, false);
  }
});
