"use client";

/**
 * DevPathClient.tsx — Shared state bridge between RepoMind and SkillGraph.
 *
 * This is the only client component at the page level. It lifts the
 * analysisResult state so SkillGraph can automatically receive the current
 * repo scan without requiring a separate path input.
 *
 * The RepoMindDashboard is modified (via the onAnalysisResult callback) to
 * notify this component whenever a scan completes.
 */

import { useState, useCallback } from "react";
import { AnalysisResult } from "@/lib/repomind-types";
import { RepoMindDashboard } from "@/components/repomind/RepoMindDashboard";
import { SkillGraphDashboard } from "@/components/skillgraph/SkillGraphDashboard";

export function DevPathClient() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const handleAnalysisResult = useCallback((result: AnalysisResult | null) => {
    setAnalysisResult(result);
  }, []);

  return (
    <>
      {/* RepoMind section */}
      <RepoMindDashboard onAnalysisResult={handleAnalysisResult} />

      {/* SkillGraph section — always rendered; uses current scan automatically */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-50 font-mono text-xs font-bold text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400">
              SG
            </span>
            <h2 className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
              SkillGraph: Job Description Skill Matcher
            </h2>
          </div>
          <span className="text-xs text-zinc-500 dark:text-zinc-400">
            {analysisResult
              ? `Using scan: ${analysisResult.repo_path.split("/").slice(-2).join("/")}`
              : "No repo scan active — JD-only mode"}
          </span>
        </div>
        <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <SkillGraphDashboard analysisResult={analysisResult} />
        </div>
      </section>
    </>
  );
}

