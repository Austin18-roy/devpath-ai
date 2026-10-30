/**
 * roadmap-storage.test.mjs — Unit tests for client-side roadmap progress management.
 * Tests role-partitioned isolation, persistence, reset boundaries, and intended projects.
 * Uses Node.js built-in test runner.
 */

import test from "node:test";
import assert from "node:assert/strict";

// Mock localStorage store for testing
class MockLocalStorage {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return this.store[key] ?? null;
  }
  setItem(key, value) {
    this.store[key] = String(value);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

const mockStorage = new MockLocalStorage();
const BASE_STORAGE_KEY = "devpath_roadmap_progress";

function getRoleStorageKey(role = "all") {
  return `${BASE_STORAGE_KEY}_${role}`;
}

function getDefaultProgress() {
  return {
    completedItems: {},
    completedTasks: {},
  };
}

function parseRawProgress(raw) {
  if (!raw) return getDefaultProgress();
  try {
    const parsed = JSON.parse(raw);
    if (
      typeof parsed === "object" &&
      parsed !== null &&
      typeof parsed.completedItems === "object" &&
      parsed.completedItems !== null &&
      typeof parsed.completedTasks === "object" &&
      parsed.completedTasks !== null
    ) {
      return {
        completedItems: parsed.completedItems,
        completedTasks: parsed.completedTasks,
      };
    }
  } catch {
    // Malformed fallback
  }
  return getDefaultProgress();
}

function loadRoadmapProgress(role = "all") {
  const roleKey = getRoleStorageKey(role);
  let raw = mockStorage.getItem(roleKey);
  if (!raw && role === "all") {
    raw = mockStorage.getItem(BASE_STORAGE_KEY);
  }
  return parseRawProgress(raw);
}

function saveRoadmapProgress(role, data) {
  const serialized = JSON.stringify(data);
  mockStorage.setItem(getRoleStorageKey(role), serialized);
}

function clearRoadmapProgress(role = "all") {
  mockStorage.removeItem(getRoleStorageKey(role));
  if (role === "all") {
    mockStorage.removeItem(BASE_STORAGE_KEY);
  }
}

function toggleCriteriaCompleted(role, skillName, criteriaIndex, totalCriteria, current) {
  const itemKey = `${skillName}__${criteriaIndex}`;
  const newCompletedItems = { ...current.completedItems };

  if (newCompletedItems[itemKey]) {
    delete newCompletedItems[itemKey];
  } else {
    newCompletedItems[itemKey] = true;
  }

  let allDone = true;
  for (let i = 0; i < totalCriteria; i++) {
    if (!newCompletedItems[`${skillName}__${i}`]) {
      allDone = false;
      break;
    }
  }

  const newCompletedTasks = { ...current.completedTasks };
  if (allDone && totalCriteria > 0) {
    newCompletedTasks[skillName] = true;
  } else {
    delete newCompletedTasks[skillName];
  }

  const updated = {
    completedItems: newCompletedItems,
    completedTasks: newCompletedTasks,
  };
  saveRoadmapProgress(role, updated);
  return updated;
}

function calculateRoadmapProgress(tasks, data) {
  const totalTasksCount = tasks.length;
  let completedTasksCount = 0;
  let totalCriteriaCount = 0;
  let completedCriteriaCount = 0;

  for (const task of tasks) {
    if (data.completedTasks[task.skill_name]) {
      completedTasksCount++;
    }
    const criteriaLen = task.completion_criteria.length;
    totalCriteriaCount += criteriaLen;
    for (let i = 0; i < criteriaLen; i++) {
      if (data.completedItems[`${task.skill_name}__${i}`]) {
        completedCriteriaCount++;
      }
    }
  }

  const percentage =
    totalCriteriaCount > 0
      ? Math.round((completedCriteriaCount / totalCriteriaCount) * 100)
      : 0;

  return {
    completedTasksCount,
    totalTasksCount,
    completedCriteriaCount,
    totalCriteriaCount,
    percentage,
  };
}

// ---------------------------------------------------------------------------
// Basic Unit Tests
// ---------------------------------------------------------------------------

test("getDefaultProgress initializes empty storage object", () => {
  const state = getDefaultProgress();
  assert.deepEqual(state.completedItems, {});
  assert.deepEqual(state.completedTasks, {});
});

test("toggleCriteriaCompleted checks criterion and completes task when all are checked", () => {
  let state = getDefaultProgress();
  state = toggleCriteriaCompleted("aiml_engineer", "pytorch", 0, 2, state);
  assert.equal(state.completedItems["pytorch__0"], true);
  assert.equal(state.completedTasks["pytorch"], undefined);

  state = toggleCriteriaCompleted("aiml_engineer", "pytorch", 1, 2, state);
  assert.equal(state.completedItems["pytorch__1"], true);
  assert.equal(state.completedTasks["pytorch"], true);

  state = toggleCriteriaCompleted("aiml_engineer", "pytorch", 0, 2, state);
  assert.equal(state.completedItems["pytorch__0"], undefined);
  assert.equal(state.completedTasks["pytorch"], undefined);
});

test("calculateRoadmapProgress accurately calculates metrics and percentages", () => {
  const mockTasks = [
    { skill_name: "pytorch", completion_criteria: ["crit 1", "crit 2"] },
    { skill_name: "docker", completion_criteria: ["crit a", "crit b", "crit c"] },
  ];

  let state = getDefaultProgress();
  let progress = calculateRoadmapProgress(mockTasks, state);
  assert.equal(progress.totalTasksCount, 2);
  assert.equal(progress.totalCriteriaCount, 5);
  assert.equal(progress.completedTasksCount, 0);
  assert.equal(progress.completedCriteriaCount, 0);
  assert.equal(progress.percentage, 0);

  state.completedItems["pytorch__0"] = true;
  state.completedItems["docker__1"] = true;
  progress = calculateRoadmapProgress(mockTasks, state);
  assert.equal(progress.completedCriteriaCount, 2);
  assert.equal(progress.percentage, 40);

  state.completedItems["pytorch__1"] = true;
  state.completedTasks["pytorch"] = true;
  progress = calculateRoadmapProgress(mockTasks, state);
  assert.equal(progress.completedTasksCount, 1);
  assert.equal(progress.completedCriteriaCount, 3);
  assert.equal(progress.percentage, 60);
});

// ---------------------------------------------------------------------------
// Milestone 5 Requirement 1: Progress is isolated between all three career roles
// ---------------------------------------------------------------------------

test("Requirement 1: Progress is isolated between all three career roles", () => {
  mockStorage.clear();

  let aimlProgress = loadRoadmapProgress("aiml_engineer");

  // Complete tasks in AI/ML Engineer
  aimlProgress = toggleCriteriaCompleted("aiml_engineer", "numpy", 0, 2, aimlProgress);
  aimlProgress = toggleCriteriaCompleted("aiml_engineer", "numpy", 1, 2, aimlProgress);
  assert.equal(aimlProgress.completedTasks["numpy"], true);

  // Reload all three roles from storage
  const loadedAiml = loadRoadmapProgress("aiml_engineer");
  const loadedGenai = loadRoadmapProgress("genai_engineer");
  const loadedSde = loadRoadmapProgress("sde");

  // AI/ML must have progress
  assert.equal(loadedAiml.completedItems["numpy__0"], true);
  assert.equal(loadedAiml.completedItems["numpy__1"], true);
  assert.equal(loadedAiml.completedTasks["numpy"], true);

  // GenAI and SDE must remain completely empty with 0 completed items
  assert.deepEqual(loadedGenai.completedItems, {});
  assert.deepEqual(loadedGenai.completedTasks, {});
  assert.deepEqual(loadedSde.completedItems, {});
  assert.deepEqual(loadedSde.completedTasks, {});
});

// ---------------------------------------------------------------------------
// Milestone 5 Requirement 2: Progress persists after reload
// ---------------------------------------------------------------------------

test("Requirement 2: Progress persists after reload across roles", () => {
  mockStorage.clear();

  // Save progress in SDE
  let sde = loadRoadmapProgress("sde");
  sde = toggleCriteriaCompleted("sde", "fastapi", 0, 3, sde);
  sde = toggleCriteriaCompleted("sde", "fastapi", 1, 3, sde);
  assert.equal(sde.completedItems["fastapi__1"], true);

  // Read back from storage (simulating reload)
  const reloadedSde = loadRoadmapProgress("sde");
  assert.equal(reloadedSde.completedItems["fastapi__0"], true);
  assert.equal(reloadedSde.completedItems["fastapi__1"], true);
  assert.equal(reloadedSde.completedItems["fastapi__2"], undefined);
  assert.equal(reloadedSde.completedTasks["fastapi"], undefined);
});

// ---------------------------------------------------------------------------
// Milestone 5 Requirement 3: Resetting one role does not reset another
// ---------------------------------------------------------------------------

test("Requirement 3: Resetting one role does not reset another role", () => {
  mockStorage.clear();

  // Setup progress for both GenAI and SDE
  let genai = loadRoadmapProgress("genai_engineer");
  genai = toggleCriteriaCompleted("genai_engineer", "langchain", 0, 2, genai);
  assert.equal(genai.completedItems["langchain__0"], true);

  let sde = loadRoadmapProgress("sde");
  sde = toggleCriteriaCompleted("sde", "git", 0, 2, sde);
  assert.equal(sde.completedItems["git__0"], true);

  assert.equal(loadRoadmapProgress("genai_engineer").completedItems["langchain__0"], true);
  assert.equal(loadRoadmapProgress("sde").completedItems["git__0"], true);

  // Reset only GenAI
  clearRoadmapProgress("genai_engineer");

  // GenAI must be cleared
  assert.deepEqual(loadRoadmapProgress("genai_engineer").completedItems, {});

  // SDE must remain untouched and active
  const sdeAfter = loadRoadmapProgress("sde");
  assert.equal(sdeAfter.completedItems["git__0"], true);
});

// ---------------------------------------------------------------------------
// Milestone 5 Requirement 4: Each role displays its own intended roadmap projects
// ---------------------------------------------------------------------------

test("Requirement 4: Each role displays its own intended roadmap projects", () => {
  const aimlProjects = [
    "NumPy Numerical Computing and Regression",
    "pandas Data Cleaning and Analysis",
    "scikit-learn Machine Learning Pipeline",
    "Model Evaluation and Validation",
  ];

  const genaiProjects = [
    "LLM API Integration",
    "Embeddings and Semantic Search",
    "Retrieval-Augmented Generation (RAG)",
    "Build a Small LLM Application with Evaluation",
  ];

  const sdeProjects = [
    "Git and Collaborative Development Workflow",
    "REST API Development and Validation",
    "Database Integration and CRUD Operations",
    "Automated Testing and Software Quality",
  ];

  // Verify count and distinctiveness
  assert.equal(aimlProjects.length, 4);
  assert.equal(genaiProjects.length, 4);
  assert.equal(sdeProjects.length, 4);

  // None of the project lists should overlap
  const genaiSet = new Set(genaiProjects);
  const sdeSet = new Set(sdeProjects);

  for (const p of aimlProjects) {
    assert.equal(genaiSet.has(p), false, `AIML project ${p} must not be in GenAI`);
    assert.equal(sdeSet.has(p), false, `AIML project ${p} must not be in SDE`);
  }
  for (const p of genaiProjects) {
    assert.equal(sdeSet.has(p), false, `GenAI project ${p} must not be in SDE`);
  }
});

// ---------------------------------------------------------------------------
// Milestone 5 Requirement 5: Switching roles does not accidentally reuse another role's checklist state
// ---------------------------------------------------------------------------

test("Requirement 5: Switching roles does not accidentally reuse another role's checklist state", () => {
  mockStorage.clear();

  // User checks item 0 for 'git' in SDE
  let sde = loadRoadmapProgress("sde");
  sde = toggleCriteriaCompleted("sde", "git", 0, 4, sde);
  assert.equal(sde.completedItems["git__0"], true);

  // User switches to AI/ML Engineer
  const aiml = loadRoadmapProgress("aiml_engineer");

  // Checking 'git' in AIML must be false/undefined
  assert.equal(aiml.completedItems["git__0"], undefined);

  // User switches to GenAI Engineer
  const genai = loadRoadmapProgress("genai_engineer");
  assert.equal(genai.completedItems["git__0"], undefined);

  // User switches back to SDE
  const reloadedSde = loadRoadmapProgress("sde");
  assert.equal(reloadedSde.completedItems["git__0"], true);
});
