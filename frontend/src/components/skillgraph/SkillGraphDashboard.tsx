"use client";

import { useState, useCallback } from "react";
import { AnalysisResult } from "@/lib/repomind-types";
import { SkillMatchResponse } from "@/lib/skillgraph-types";
import { matchJobSkills } from "@/lib/skillgraph-api";
import { JobDescriptionInput } from "./JobDescriptionInput";
import { SkillSummaryBar } from "./SkillSummaryBar";
import { SkillResultCard } from "./SkillResultCard";
import { GapRecommendations } from "./GapRecommendations";

interface SkillGraphDashboardProps {
  /** Pass the current RepoMind AnalysisResult so SkillGraph can use it
   *  without requiring a separate repository path input. */
  analysisResult: AnalysisResult | null;
}

export function SkillGraphDashboard({ analysisResult }: SkillGraphDashboardProps) {
  const [jobDescription, setJobDescription] = useState("");
  const [matchResult, setMatchResult] = useState<SkillMatchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showGaps, setShowGaps] = useState(false);

  const handleAnalyze = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setMatchResult(null);
    setShowGaps(false);

    try {
      const result = await matchJobSkills({
        job_description: jobDescription,
        analysis_result: analysisResult ?? null,
      });
      setMatchResult(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to analyze job description."
      );
    } finally {
      setIsLoading(false);
    }
  }, [jobDescription, analysisResult]);

  const allSkills = matchResult
    ? [...matchResult.skills_required, ...matchResult.skills_preferred]
    : [];
  const gapCount = allSkills.filter((s) => s.recommendation).length;

  return (
    <div className="space-y-5">
      {/* Job description input */}
      <JobDescriptionInput
        value={jobDescription}
        onChange={setJobDescription}
        onSubmit={handleAnalyze}
        isLoading={isLoading}
        hasAnalysis={analysisResult !== null}
        error={error}
      />

      {/* Results */}
      {matchResult && (
        <div className="space-y-6">
          {/* Summary bar */}
          <SkillSummaryBar summary={matchResult.summary} />

          {/* Skills — required first, then preferred */}
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
                Try pasting a longer description that mentions specific technologies.
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

          {/* Disclaimer */}
          <p className="rounded-lg border border-zinc-100 bg-zinc-50 px-3 py-2 text-xs italic leading-relaxed text-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-500">
            {matchResult.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}

