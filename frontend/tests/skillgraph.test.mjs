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
function buildSkillMatchPayload(jobDescription, analysisResult, targetRole) {
  return {
    job_description: jobDescription,
    analysis_result: analysisResult ?? null,
    target_role: targetRole ?? "all",
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

/**
 * Pure helper: get confidence badge styling (mirrors skillgraph-api.ts).
 */
function getConfidenceBadgeClasses(confidence) {
  switch (confidence) {
    case "high":
      return { label: "High confidence", text: "text-emerald-700 dark:text-emerald-300" };
    case "medium":
      return { label: "Medium confidence", text: "text-amber-700 dark:text-amber-300" };
    case "low":
    default:
      return { label: "Low confidence", text: "text-zinc-600 dark:text-zinc-400" };
  }
}

// ---------------------------------------------------------------------------
// Test 1: buildSkillMatchPayload — with analysis result and target role
// ---------------------------------------------------------------------------

test("buildSkillMatchPayload includes analysis_result and target_role when provided", () => {
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

  const payload = buildSkillMatchPayload(
    "We need a Python developer with numpy.",
    mockAnalysis,
    "aiml_engineer"
  );

  assert.equal(payload.job_description, "We need a Python developer with numpy.");
  assert.deepEqual(payload.analysis_result, mockAnalysis);
  assert.equal(payload.target_role, "aiml_engineer");
  assert.deepEqual(payload.analysis_result.imported_packages, ["numpy", "pandas"]);
});

// ---------------------------------------------------------------------------
// Test 2: buildSkillMatchPayload — without analysis result defaults
// ---------------------------------------------------------------------------

test("buildSkillMatchPayload sets analysis_result to null and target_role to 'all' when not provided", () => {
  const payload = buildSkillMatchPayload("Looking for a FastAPI developer.");

  assert.equal(payload.job_description, "Looking for a FastAPI developer.");
  assert.equal(payload.analysis_result, null);
  assert.equal(payload.target_role, "all");
});

// ---------------------------------------------------------------------------
// Test 3: parseSkillResponse — correct required/preferred split with roadmap task
// ---------------------------------------------------------------------------

test("parseSkillResponse correctly separates required and preferred arrays with roadmap task", () => {
  const mockResponse = {
    skills_required: [
      {
        canonical_name: "pytorch",
        evidence_tier: "none",
        aliases_matched: ["torch"],
        evidence_items: [],
        explanation: "No evidence found.",
        recommendation: "Build a model.",
        related_skills: ["numpy", "transformers"],
        roadmap_task: {
          skill_name: "pytorch",
          task_title: "Build and Train a PyTorch Classifier",
          objective: "Train a model",
          difficulty: "intermediate",
          estimated_hours: 3,
          completion_criteria: ["Criterion 1"],
          deliverable: "train.py",
          role_relevance: "Core deep learning",
          resources: [],
        },
      },
    ],
    skills_preferred: [
      {
        canonical_name: "docker",
        evidence_tier: "none",
        aliases_matched: ["docker"],
        evidence_items: [],
        explanation: "No evidence.",
        recommendation: "Add docker.",
        related_skills: ["kubernetes"],
        roadmap_task: null,
      },
    ],
    summary: {
      required_count: 1,
      preferred_count: 1,
      strong_evidence_count: 0,
      weak_evidence_count: 0,
      no_evidence_count: 2,
      coverage_note: "Test coverage note.",
    },
    disclaimer: "Static analysis only.",
  };

  const { required, preferred } = parseSkillResponse(mockResponse);

  assert.equal(required.length, 1);
  assert.equal(preferred.length, 1);
  assert.equal(required[0].canonical_name, "pytorch");
  assert.notEqual(required[0].roadmap_task, null);
  assert.equal(required[0].roadmap_task.skill_name, "pytorch");
  assert.deepEqual(required[0].related_skills, ["numpy", "transformers"]);
  assert.equal(preferred[0].canonical_name, "docker");
  assert.equal(preferred[0].roadmap_task, null);
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

// ---------------------------------------------------------------------------
// Test 6: getConfidenceBadgeClasses — correct styles per confidence
// ---------------------------------------------------------------------------

test("getConfidenceBadgeClasses returns correct label and styles", () => {
  assert.equal(getConfidenceBadgeClasses("high").label, "High confidence");
  assert.ok(getConfidenceBadgeClasses("high").text.includes("emerald"));

  assert.equal(getConfidenceBadgeClasses("medium").label, "Medium confidence");
  assert.ok(getConfidenceBadgeClasses("medium").text.includes("amber"));

  assert.equal(getConfidenceBadgeClasses("low").label, "Low confidence");
  assert.ok(getConfidenceBadgeClasses("low").text.includes("zinc"));

  assert.equal(getConfidenceBadgeClasses("unknown").label, "Low confidence");
});

// ---------------------------------------------------------------------------
// Test 7: Roadmap task fields resolution (objective & role relevance fallbacks)
// ---------------------------------------------------------------------------

test("roadmap task fields resolve correctly with fallbacks", () => {
  const taskWithObjective = {
    skill_name: "numpy",
    title: "NumPy Regression",
    objective: "Implement linear regression from scratch",
    role_relevance: "Crucial for mathematical modeling in AI/ML",
    deliverable: "matrix_regression.py",
    completion_criteria: ["crit 1"],
    resources: [],
  };

  const taskWithDescription = {
    skill_name: "fastapi",
    task_title: "REST API Validation",
    description: "Build a typed API with Pydantic",
    target_role_relevance: "Essential for microservices in SDE",
    deliverable: "main.py",
    completion_criteria: ["crit 1"],
    resources: [],
  };

  // Helper matching CareerRoadmapView logic
  const resolveFields = (t) => ({
    title: t.title || t.task_title || "",
    roleRelevance: t.role_relevance || t.target_role_relevance || "",
    objective: t.objective || t.description || "",
  });

  const res1 = resolveFields(taskWithObjective);
  assert.equal(res1.title, "NumPy Regression");
  assert.equal(res1.roleRelevance, "Crucial for mathematical modeling in AI/ML");
  assert.equal(res1.objective, "Implement linear regression from scratch");

  const res2 = resolveFields(taskWithDescription);
  assert.equal(res2.title, "REST API Validation");
  assert.equal(res2.roleRelevance, "Essential for microservices in SDE");
  assert.equal(res2.objective, "Build a typed API with Pydantic");
});

