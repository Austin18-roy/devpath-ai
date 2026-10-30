"use client";

import { useCallback, useMemo, useSyncExternalStore } from "react";
import { RoadmapTask, SkillResult, TargetRole } from "@/lib/skillgraph-types";
import {
  calculateRoadmapProgress,
  clearRoadmapProgress,
  getRoadmapProgressSnapshot,
  getServerRoadmapProgressSnapshot,
  isCriteriaCompleted,
  isTaskCompleted,
  parseRawProgress,
  subscribeRoadmapProgress,
  toggleCriteriaCompleted,
} from "@/lib/roadmap-storage";

interface CareerRoadmapViewProps {
  tasks: RoadmapTask[];
  preferredSkills?: SkillResult[];
  targetRole: TargetRole;
}

const ROLE_LABELS: Record<TargetRole, string> = {
  all: "All Roles",
  aiml_engineer: "AI/ML Engineer",
  genai_engineer: "Generative AI Engineer",
  sde: "Software Development Engineer",
};

export function CareerRoadmapView({
  tasks,
  preferredSkills = [],
  targetRole,
}: CareerRoadmapViewProps) {
  // Use React 18/19 external store hook to read from role-specific localStorage reactively
  const getSnapshot = useCallback(() => getRoadmapProgressSnapshot(targetRole), [targetRole]);
  const rawProgress = useSyncExternalStore(
    subscribeRoadmapProgress,
    getSnapshot,
    getServerRoadmapProgressSnapshot
  );

  const progress = useMemo(() => parseRawProgress(rawProgress), [rawProgress]);

  const handleToggleCriteria = (skillName: string, criteriaIndex: number, total: number) => {
    toggleCriteriaCompleted(targetRole, skillName, criteriaIndex, total, progress);
  };

  const handleReset = () => {
    if (confirm(`Reset checklist progress for ${ROLE_LABELS[targetRole]}?`)) {
      clearRoadmapProgress(targetRole);
    }
  };

  const stats = calculateRoadmapProgress(tasks, progress);

  const getDifficultyBadge = (difficulty: string) => {
    switch (difficulty) {
      case "beginner":
        return "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800";
      case "advanced":
        return "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/50 dark:text-purple-300 dark:border-purple-800";
      case "intermediate":
      default:
        return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800";
    }
  };

  if (tasks.length === 0) {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-6 text-center dark:border-emerald-900/50 dark:bg-emerald-950/20">
        <h4 className="text-base font-semibold text-emerald-800 dark:text-emerald-300">
          🎉 No Required Skill Gaps Detected
        </h4>
        <p className="mt-1 text-xs text-emerald-700 dark:text-emerald-400">
          Your repository demonstrates strong evidence for all required skills identified in this job description.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Roadmap Overview & Progress Bar */}
      <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
                Actionable Portfolio Roadmap
              </h3>
              <span className="rounded-md bg-zinc-100 px-2 py-0.5 text-[11px] font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                Tailored for: {ROLE_LABELS[targetRole]}
              </span>
            </div>
            <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
              Complete these targeted mini-projects to build demonstrable repository evidence for missing or weak required skills.
            </p>
          </div>
          {stats.completedCriteriaCount > 0 && (
            <button
              onClick={handleReset}
              className="text-xs text-zinc-400 hover:text-zinc-600 underline dark:text-zinc-500 dark:hover:text-zinc-300"
            >
              Reset this role&apos;s progress
            </button>
          )}
        </div>

        {/* Progress bar */}
        <div className="mt-4 space-y-1.5">
          <div className="flex justify-between text-xs font-medium text-zinc-600 dark:text-zinc-400">
            <span>
              {stats.completedTasksCount} of {stats.totalTasksCount} projects completed (
              {stats.completedCriteriaCount}/{stats.totalCriteriaCount} criteria)
            </span>
            <span className="font-semibold text-indigo-600 dark:text-indigo-400">
              {stats.percentage}%
            </span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
            <div
              className="h-full rounded-full bg-indigo-600 transition-all duration-300 dark:bg-indigo-500"
              style={{ width: `${stats.percentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Task Cards */}
      <div className="space-y-4">
        {tasks.map((task) => {
          const taskDone = isTaskCompleted(task.skill_name, progress);
          return (
            <div
              key={task.skill_name}
              className={`rounded-xl border p-5 transition-all shadow-sm ${
                taskDone
                  ? "border-emerald-300 bg-emerald-50/20 dark:border-emerald-900/60 dark:bg-emerald-950/10"
                  : "border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900"
              }`}
            >
              {/* Task Header */}
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded dark:bg-indigo-950/60 dark:text-indigo-300">
                      {task.skill_name}
                    </span>
                    <span
                      className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold capitalize ${getDifficultyBadge(
                        task.difficulty
                      )}`}
                    >
                      {task.difficulty}
                    </span>
                    <span className="text-xs text-zinc-400 dark:text-zinc-500">
                      ⏱ ~{task.estimated_hours} hrs
                    </span>
                    {taskDone && (
                      <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-800 dark:bg-emerald-950/70 dark:text-emerald-300">
                        ✓ Completed
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                    {task.title || task.task_title}
                  </h4>
                </div>
              </div>

              {/* Role relevance note */}
              <div className="mt-2.5 rounded-lg bg-zinc-50 p-2.5 text-xs text-zinc-600 dark:bg-zinc-800/60 dark:text-zinc-300">
                <span className="font-semibold text-zinc-800 dark:text-zinc-200">
                  Role Relevance:{" "}
                </span>
                {task.role_relevance || task.target_role_relevance}
              </div>

              {/* Objective & Deliverable */}
              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div className="rounded-lg border border-zinc-100 p-2.5 dark:border-zinc-800 dark:bg-zinc-800/30">
                  <span className="font-semibold text-zinc-700 dark:text-zinc-300 block mb-1">
                    🎯 Objective
                  </span>
                  <p className="text-zinc-600 dark:text-zinc-400">
                    {task.objective || task.description}
                  </p>
                </div>
                <div className="rounded-lg border border-zinc-100 p-2.5 dark:border-zinc-800 dark:bg-zinc-800/30">
                  <span className="font-semibold text-zinc-700 dark:text-zinc-300 block mb-1">
                    📦 Deliverable Artifact
                  </span>
                  <p className="text-zinc-600 dark:text-zinc-400">{task.deliverable}</p>
                </div>
              </div>

              {/* Completion Criteria Checklist */}
              <div className="mt-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-2">
                  Completion Checklist
                </p>
                <div className="space-y-1.5">
                  {task.completion_criteria.map((criterion, idx) => {
                    const checked = isCriteriaCompleted(task.skill_name, idx, progress);
                    return (
                      <label
                        key={idx}
                        className={`flex items-start gap-2.5 rounded-lg p-2 text-xs cursor-pointer select-none transition-colors ${
                          checked
                            ? "bg-emerald-50 text-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200"
                            : "hover:bg-zinc-50 text-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800/50"
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() =>
                            handleToggleCriteria(
                              task.skill_name,
                              idx,
                              task.completion_criteria.length
                            )
                          }
                          className="mt-0.5 rounded border-zinc-300 text-indigo-600 focus:ring-indigo-500 dark:border-zinc-700 dark:bg-zinc-800"
                        />
                        <span className={checked ? "line-through opacity-80" : ""}>
                          {criterion}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Learning Resources */}
              {task.resources && task.resources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-zinc-100 dark:border-zinc-800">
                  <p className="text-[11px] font-semibold text-zinc-500 dark:text-zinc-400 mb-2">
                    Free Official Resources:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {task.resources.map((res) => (
                      <a
                        key={res.url}
                        href={res.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 rounded-md border border-zinc-200 bg-zinc-50 px-2.5 py-1 text-xs text-indigo-600 hover:border-indigo-300 hover:bg-indigo-50/50 hover:text-indigo-700 dark:border-zinc-700 dark:bg-zinc-800/80 dark:text-indigo-300 dark:hover:bg-indigo-950/40"
                      >
                        <span>📖</span>
                        <span>{res.title}</span>
                        <span className="text-[10px] text-zinc-400">↗</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Preferred Skills as Optional Recommendations */}
      {preferredSkills.length > 0 && (
        <div className="rounded-xl border border-dashed border-zinc-300 bg-zinc-50/60 p-4 dark:border-zinc-700 dark:bg-zinc-900/40">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Preferred Qualifications (Optional Boost)
          </h4>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            These skills are listed as nice-to-have in the job description. Tackling them will make your portfolio stand out even further:
          </p>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2">
            {preferredSkills.map((p) => (
              <div
                key={p.canonical_name}
                className="rounded-lg bg-white p-2.5 border border-zinc-200 dark:border-zinc-800 dark:bg-zinc-800/60 text-xs"
              >
                <div className="flex items-center justify-between font-mono font-bold text-zinc-800 dark:text-zinc-200">
                  <span>{p.canonical_name}</span>
                  <span className="font-sans text-[11px] font-normal text-zinc-500 dark:text-zinc-400">
                    Status: {p.evidence_tier}
                  </span>
                </div>
                {p.recommendation && (
                  <p className="mt-1 text-zinc-600 dark:text-zinc-400">{p.recommendation}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
