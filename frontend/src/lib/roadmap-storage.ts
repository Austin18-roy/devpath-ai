/**
 * roadmap-storage.ts — Client-side progress tracking for Career Roadmap tasks.
 * Stores checklist completion in localStorage partitioned by career role.
 * Ensures each career role maintains completely isolated progress.
 * Resilient to missing, uninitialized, or corrupted storage.
 * Provides useSyncExternalStore integration for zero-render-cascade React 19 reactivity.
 */

import { TargetRole } from "./skillgraph-types";

export interface RoadmapProgressData {
  completedItems: Record<string, boolean>;
  completedTasks: Record<string, boolean>;
}

const BASE_STORAGE_KEY = "devpath_roadmap_progress";
const PROGRESS_EVENT = "devpath_roadmap_progress_change";

/**
 * Returns the role-scoped localStorage key.
 * e.g. devpath_roadmap_progress_aiml_engineer
 */
export function getRoleStorageKey(role: TargetRole = "all"): string {
  return `${BASE_STORAGE_KEY}_${role}`;
}

/**
 * Returns the default empty progress state.
 */
export function getDefaultProgress(): RoadmapProgressData {
  return {
    completedItems: {},
    completedTasks: {},
  };
}

/**
 * Safely parses raw JSON or returns default empty state.
 */
export function parseRawProgress(raw: string | null): RoadmapProgressData {
  if (!raw) {
    return getDefaultProgress();
  }
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
    // Malformed JSON fallback
  }
  return getDefaultProgress();
}

/**
 * Subscribes to local storage changes for useSyncExternalStore.
 */
export function subscribeRoadmapProgress(callback: () => void): () => void {
  if (typeof window === "undefined") {
    return () => {};
  }
  window.addEventListener("storage", callback);
  window.addEventListener(PROGRESS_EVENT, callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(PROGRESS_EVENT, callback);
  };
}

/**
 * Snapshot getter for useSyncExternalStore on client for a specific role.
 * Falls back to legacy non-partitioned storage key if role is 'all' and new key is uninitialized.
 */
export function getRoadmapProgressSnapshot(role: TargetRole = "all"): string {
  if (typeof window === "undefined" || !window.localStorage) {
    return "";
  }
  const roleKey = getRoleStorageKey(role);
  const val = window.localStorage.getItem(roleKey);
  if (val != null) {
    return val;
  }
  if (role === "all") {
    return window.localStorage.getItem(BASE_STORAGE_KEY) ?? "";
  }
  return "";
}

/**
 * Server snapshot getter for useSyncExternalStore during SSR.
 */
export function getServerRoadmapProgressSnapshot(): string {
  return "";
}

/**
 * Safely loads the user's roadmap progress for a specific career role.
 */
export function loadRoadmapProgress(role: TargetRole = "all"): RoadmapProgressData {
  if (typeof window === "undefined" || !window.localStorage) {
    return getDefaultProgress();
  }

  try {
    const raw = getRoadmapProgressSnapshot(role);
    return parseRawProgress(raw);
  } catch {
    return getDefaultProgress();
  }
}

/**
 * Safely saves the user's roadmap progress for a specific career role to localStorage.
 */
export function saveRoadmapProgress(
  role: TargetRole,
  data: RoadmapProgressData
): void {
  if (typeof window === "undefined" || !window.localStorage) {
    return;
  }

  try {
    const serialized = JSON.stringify(data);
    window.localStorage.setItem(getRoleStorageKey(role), serialized);
    window.dispatchEvent(new Event(PROGRESS_EVENT));
  } catch {
    // QuotaExceededError or storage disabled in private mode
  }
}

/**
 * Toggles a single checklist criterion for a skill task within a specific career role.
 * Automatically marks the task as completed if all criteria are checked.
 */
export function toggleCriteriaCompleted(
  role: TargetRole,
  skillName: string,
  criteriaIndex: number,
  totalCriteria: number,
  current: RoadmapProgressData
): RoadmapProgressData {
  const itemKey = `${skillName}__${criteriaIndex}`;
  const newCompletedItems = { ...current.completedItems };

  if (newCompletedItems[itemKey]) {
    delete newCompletedItems[itemKey];
  } else {
    newCompletedItems[itemKey] = true;
  }

  // Check if all criteria for this task are completed
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

  const updated: RoadmapProgressData = {
    completedItems: newCompletedItems,
    completedTasks: newCompletedTasks,
  };

  saveRoadmapProgress(role, updated);
  return updated;
}

/**
 * Returns whether a specific criterion is marked as completed.
 */
export function isCriteriaCompleted(
  skillName: string,
  criteriaIndex: number,
  data: RoadmapProgressData
): boolean {
  return Boolean(data.completedItems[`${skillName}__${criteriaIndex}`]);
}

/**
 * Returns whether a task is marked as fully completed.
 */
export function isTaskCompleted(
  skillName: string,
  data: RoadmapProgressData
): boolean {
  return Boolean(data.completedTasks[skillName]);
}

/**
 * Computes overall completion statistics across a list of roadmap tasks.
 */
export function calculateRoadmapProgress(
  tasks: Array<{ skill_name: string; completion_criteria: string[] }>,
  data: RoadmapProgressData
): {
  completedTasksCount: number;
  totalTasksCount: number;
  completedCriteriaCount: number;
  totalCriteriaCount: number;
  percentage: number;
} {
  const totalTasksCount = tasks.length;
  let completedTasksCount = 0;
  let totalCriteriaCount = 0;
  let completedCriteriaCount = 0;

  for (const task of tasks) {
    if (isTaskCompleted(task.skill_name, data)) {
      completedTasksCount++;
    }
    const criteriaLen = task.completion_criteria.length;
    totalCriteriaCount += criteriaLen;
    for (let i = 0; i < criteriaLen; i++) {
      if (isCriteriaCompleted(task.skill_name, i, data)) {
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

/**
 * Resets roadmap progress in localStorage ONLY for the specified career role.
 */
export function clearRoadmapProgress(role: TargetRole = "all"): void {
  if (typeof window !== "undefined" && window.localStorage) {
    try {
      window.localStorage.removeItem(getRoleStorageKey(role));
      if (role === "all") {
        window.localStorage.removeItem(BASE_STORAGE_KEY);
      }
      window.dispatchEvent(new Event(PROGRESS_EVENT));
    } catch {
      // Storage access restricted
    }
  }
}
