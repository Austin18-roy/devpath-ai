"use client";

import { useState, useCallback } from "react";
import { AnalysisResult } from "@/lib/repomind-types";
import { RoadmapTask, SkillMatchResponse, TargetRole } from "@/lib/skillgraph-types";
import { matchJobSkills } from "@/lib/skillgraph-api";
import { JobDescriptionInput } from "./JobDescriptionInput";
import { SkillSummaryBar } from "./SkillSummaryBar";
import { SkillResultCard } from "./SkillResultCard";
import { GapRecommendations } from "./GapRecommendations";
import { CareerRoadmapView } from "./CareerRoadmapView";
import { SkillRelationshipView } from "./SkillRelationshipView";

interface SkillGraphDashboardProps {
  /** Pass the current RepoMind AnalysisResult so SkillGraph can use it
   *  without requiring a separate repository path input. */
  analysisResult: AnalysisResult | null;
}

type TabType = "skills" | "roadmap" | "network";

const ROLES: Array<{ id: TargetRole; label: string; icon: string }> = [
  { id: "all", label: "All Roles", icon: "🌐" },
  { id: "aiml_engineer", label: "AI/ML Engineer", icon: "🤖" },
  { id: "genai_engineer", label: "Generative AI Engineer", icon: "✨" },
  { id: "sde", label: "Software Development Engineer", icon: "💻" },
];

export function SkillGraphDashboard({ analysisResult }: SkillGraphDashboardProps) {
  const [jobDescription, setJobDescription] = useState("");
  const [targetRole, setTargetRole] = useState<TargetRole>(() => {
    if (typeof window !== "undefined" && window.localStorage) {
      try {
        const saved = window.localStorage.getItem("devpath_selected_role");
        if (
          saved === "aiml_engineer" ||
          saved === "genai_engineer" ||
          saved === "sde" ||
          saved === "all"
        ) {
          return saved;
        }
      } catch {
        // Storage restricted
      }
    }
    return "all";
  });
  const [matchResult, setMatchResult] = useState<SkillMatchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showGaps, setShowGaps] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>("skills");

  const runAnalysis = useCallback(
    async (roleToUse: TargetRole = targetRole) => {
      setIsLoading(true);
      setError(null);
      setMatchResult(null);
      setShowGaps(false);

      try {
        const result = await matchJobSkills({
          job_description: jobDescription,
          analysis_result: analysisResult ?? null,
          target_role: roleToUse,
        });
        setMatchResult(result);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to analyze job description."
        );
      } finally {
        setIsLoading(false);
      }
    },
    [jobDescription, analysisResult, targetRole]
  );

  const handleRoleChange = (newRole: TargetRole) => {
    setTargetRole(newRole);
    if (typeof window !== "undefined" && window.localStorage) {
      try {
        window.localStorage.setItem("devpath_selected_role", newRole);
      } catch {
        // Storage restricted
      }
    }
    if (matchResult && jobDescription.trim().length >= 20) {
      runAnalysis(newRole);
    }
  };

  const allSkills = matchResult
    ? [...matchResult.skills_required, ...matchResult.skills_preferred]
    : [];
  const gapCount = allSkills.filter((s) => s.recommendation).length;

  // Collect roadmap tasks: role_roadmap from backend takes precedence for genuinely tailored projects
  const roadmapTasks: RoadmapTask[] = matchResult
    ? (matchResult.role_roadmap && matchResult.role_roadmap.length > 0
        ? matchResult.role_roadmap
        : matchResult.skills_required
            .map((s) => s.roadmap_task)
            .filter((task): task is RoadmapTask => task !== null))
    : [];

  return (
    <div className="space-y-6">
      {/* Target Role Selector Header */}
      <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-2">
          Target Career Role
        </label>
        <div className="flex flex-wrap gap-2">
          {ROLES.map((role) => (
            <button
              key={role.id}
              type="button"
              onClick={() => handleRoleChange(role.id)}
              className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
                targetRole === role.id
                  ? "border-emerald-600 bg-emerald-50 text-emerald-800 font-semibold shadow-sm dark:border-emerald-500 dark:bg-emerald-950/60 dark:text-emerald-200 ring-2 ring-emerald-500/20"
                  : "border-zinc-200 bg-zinc-50 text-zinc-600 hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
              }`}
            >
              <span>{role.icon}</span>
              <span>{role.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Job description input */}
      <JobDescriptionInput
        value={jobDescription}
        onChange={setJobDescription}
        onSubmit={() => runAnalysis(targetRole)}
        isLoading={isLoading}
        hasAnalysis={analysisResult !== null}
        error={error}
      />

      {/* Results View */}
      {matchResult && (
        <div className="space-y-6">
          {/* Summary bar */}
          <SkillSummaryBar summary={matchResult.summary} />

          {/* Navigation Tabs */}
          <div className="flex border-b border-zinc-200 dark:border-zinc-800">
            <button
              onClick={() => setActiveTab("skills")}
              className={`flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-all ${
                activeTab === "skills"
                  ? "border-emerald-600 text-emerald-700 dark:border-emerald-400 dark:text-emerald-300"
                  : "border-transparent text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
              }`}
            >
              <span>📋</span>
              <span>Skills & Evidence</span>
              <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-semibold text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
                {allSkills.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab("roadmap")}
              className={`flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-all ${
                activeTab === "roadmap"
                  ? "border-indigo-600 text-indigo-700 dark:border-indigo-400 dark:text-indigo-300"
                  : "border-transparent text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
              }`}
            >
              <span>🚀</span>
              <span>Career Roadmap</span>
              {roadmapTasks.length > 0 && (
                <span className="rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-semibold text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                  {roadmapTasks.length} task{roadmapTasks.length > 1 ? "s" : ""}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab("network")}
              className={`flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-all ${
                activeTab === "network"
                  ? "border-purple-600 text-purple-700 dark:border-purple-400 dark:text-purple-300"
                  : "border-transparent text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
              }`}
            >
              <span>🕸️</span>
              <span>Skill Network</span>
            </button>
          </div>

          {/* TAB 1: Skills & Evidence */}
          {activeTab === "skills" && (
            <div className="space-y-6">
              {allSkills.length > 0 ? (
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
                    Skill Results ({allSkills.length})
                  </h4>
                  <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
                    {matchResult.skills_required.map((skill) => (
                      <SkillResultCard
                        key={skill.canonical_name}
                        skill={skill}
                        isRequired={true}
                      />
                    ))}
                    {matchResult.skills_preferred.map((skill) => (
                      <SkillResultCard
                        key={skill.canonical_name}
                        skill={skill}
                        isRequired={false}
                      />
                    ))}
                  </div>
                </div>
              ) : (
                <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-6 text-center dark:border-zinc-700 dark:bg-zinc-800/50">
                  <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                    No recognisable skills were found in this job description.
                  </p>
                  <p className="mt-1 text-xs text-zinc-400 dark:text-zinc-500">
                    Try pasting a description that mentions specific frameworks, languages, or tools.
                  </p>
                </div>
              )}

              {/* Gap recommendations (collapsible) */}
              {gapCount > 0 && (
                <div className="space-y-2">
                  <button
                    onClick={() => setShowGaps((prev) => !prev)}
                    className="flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:text-emerald-800 dark:text-emerald-400 dark:hover:text-emerald-300"
                  >
                    <span>{showGaps ? "▼" : "▶"}</span>
                    {showGaps ? "Hide" : "Show"} Gap Recommendations ({gapCount})
                  </button>
                  {showGaps && (
                    <GapRecommendations
                      requiredSkills={matchResult.skills_required}
                      preferredSkills={matchResult.skills_preferred}
                    />
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Career Roadmap */}
          {activeTab === "roadmap" && (
            <CareerRoadmapView
              tasks={roadmapTasks}
              preferredSkills={matchResult.skills_preferred}
              targetRole={targetRole}
            />
          )}

          {/* TAB 3: Skill Network */}
          {activeTab === "network" && (
            <SkillRelationshipView skills={allSkills} />
          )}

          {/* Disclaimer */}
          <p className="rounded-lg border border-zinc-100 bg-zinc-50 px-3 py-2 text-xs italic leading-relaxed text-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-500">
            {matchResult.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}
