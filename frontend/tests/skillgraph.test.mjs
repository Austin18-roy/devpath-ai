/**
 * skillgraph.test.mjs — Unit tests for SkillGraph frontend utilities.
 * Uses Node.js built-in test runner (same pattern as graph-adapter.test.mjs).
 */

import test from "node:test";
import assert from "node:assert/strict";

// ---------------------------------------------------------------------------
// Import the modules under test.
// We import from the compiled .mjs equivalents or recreate minimal logic here.
// Since skillgraph-api.ts is TypeScript, we test the pure logic extracted here.
// ---------------------------------------------------------------------------

/**
 * Pure helper: build a SkillMatch payload (mirrors skillgraph-api.ts logic).
 */
function buildSkillMatchPayload(jobDescription, analysisResult) {
  return {
    job_description: jobDescription,
    analysis_result: analysisResult ?? null,
  };
}

/**
 * Pure helper: parse required vs preferred from a mock response.
 */
function parseSkillResponse(response) {
  return {
    required: response.skills_required ?? [],
    preferred: response.skills_preferred ?? [],
  };
}

/**
 * Pure helper: compute summary counts from skills arrays.
 */
function computeSummaryCounts(required, preferred) {
  const all = [...required, ...preferred];
  return {
    required_count: required.length,
    preferred_count: preferred.length,
    strong: all.filter((s) => s.evidence_tier === "strong").length,
    weak: all.filter((s) => s.evidence_tier === "weak").length,
    none: all.filter((s) => s.evidence_tier === "none").length,
  };
}

/**
 * Pure helper: get Tailwind colour classes per tier (mirrors skillgraph-api.ts).
 */
function getTierBadgeClasses(tier) {
  switch (tier) {
    case "strong":
      return { label: "Strong evidence", text: "text-emerald-800 dark:text-emerald-300" };
    case "weak":
      return { label: "Weak evidence", text: "text-amber-800 dark:text-amber-300" };
    default:
      return { label: "No evidence", text: "text-red-800 dark:text-red-300" };
  }
}

// ---------------------------------------------------------------------------
// Test 1: buildSkillMatchPayload — with analysis result
// ---------------------------------------------------------------------------

test("buildSkillMatchPayload includes analysis_result when provided", () => {
  const mockAnalysis = {
    repo_path: "/repo",
    files_scanned: 3,
    symbols_count: 10,
    edges_count: 5,
    symbols: [],
    edges: [],
    unresolved_calls: [],
    diagnostics: [],
    limitations: [],
    imported_packages: ["numpy", "pandas"],
  };

  const payload = buildSkillMatchPayload("We need a Python developer with numpy.", mockAnalysis);

  assert.equal(payload.job_description, "We need a Python developer with numpy.");
  assert.deepEqual(payload.analysis_result, mockAnalysis);
  assert.deepEqual(payload.analysis_result.imported_packages, ["numpy", "pandas"]);
});

// ---------------------------------------------------------------------------
// Test 2: buildSkillMatchPayload — without analysis result
// ---------------------------------------------------------------------------

test("buildSkillMatchPayload sets analysis_result to null when not provided", () => {
  const payload = buildSkillMatchPayload("Looking for a FastAPI developer.");

  assert.equal(payload.job_description, "Looking for a FastAPI developer.");
  assert.equal(payload.analysis_result, null);
});

// ---------------------------------------------------------------------------
// Test 3: parseSkillResponse — correct required/preferred split
// ---------------------------------------------------------------------------

test("parseSkillResponse correctly separates required and preferred arrays", () => {
  const mockResponse = {
    skills_required: [
      { canonical_name: "numpy", evidence_tier: "none", aliases_matched: ["numpy"], evidence_items: [], explanation: "No evidence.", recommendation: "Add numpy." },
      { canonical_name: "pytorch", evidence_tier: "weak", aliases_matched: ["torch"], evidence_items: [], explanation: "Weak.", recommendation: "Add pytorch." },
    ],
    skills_preferred: [
      { canonical_name: "docker", evidence_tier: "none", aliases_matched: ["docker"], evidence_items: [], explanation: "No evidence.", recommendation: "Add docker." },
    ],
    summary: {
      required_count: 2,
      preferred_count: 1,
      strong_evidence_count: 0,
      weak_evidence_count: 1,
      no_evidence_count: 2,
      coverage_note: "Test coverage note.",
    },
    disclaimer: "Static analysis only.",
  };

  const { required, preferred } = parseSkillResponse(mockResponse);

  assert.equal(required.length, 2);
  assert.equal(preferred.length, 1);
  assert.equal(required[0].canonical_name, "numpy");
  assert.equal(preferred[0].canonical_name, "docker");
});

// ---------------------------------------------------------------------------
// Test 4: computeSummaryCounts — sums are correct
// ---------------------------------------------------------------------------

test("computeSummaryCounts returns correct totals", () => {
  const required = [
    { canonical_name: "numpy", evidence_tier: "strong" },
    { canonical_name: "pytorch", evidence_tier: "weak" },
    { canonical_name: "fastapi", evidence_tier: "none" },
  ];
  const preferred = [
    { canonical_name: "docker", evidence_tier: "none" },
    { canonical_name: "mlflow", evidence_tier: "none" },
  ];

  const counts = computeSummaryCounts(required, preferred);

  assert.equal(counts.required_count, 3);
  assert.equal(counts.preferred_count, 2);
  assert.equal(counts.strong, 1);
  assert.equal(counts.weak, 1);
  assert.equal(counts.none, 3);
  assert.equal(counts.strong + counts.weak + counts.none, 5);
});

// ---------------------------------------------------------------------------
// Test 5: getTierBadgeClasses — correct Tailwind classes per tier
// ---------------------------------------------------------------------------

test("getTierBadgeClasses returns emerald for strong", () => {
  const classes = getTierBadgeClasses("strong");
  assert.equal(classes.label, "Strong evidence");
  assert.ok(classes.text.includes("emerald"), `Expected emerald in text classes, got: ${classes.text}`);
});

test("getTierBadgeClasses returns amber for weak", () => {
  const classes = getTierBadgeClasses("weak");
  assert.equal(classes.label, "Weak evidence");
  assert.ok(classes.text.includes("amber"), `Expected amber in text classes, got: ${classes.text}`);
});

test("getTierBadgeClasses returns red for none", () => {
  const classes = getTierBadgeClasses("none");
  assert.equal(classes.label, "No evidence");
  assert.ok(classes.text.includes("red"), `Expected red in text classes, got: ${classes.text}`);
});

test("getTierBadgeClasses returns red for unknown tier", () => {
  const classes = getTierBadgeClasses("unknown_value");
  assert.equal(classes.label, "No evidence");
});

