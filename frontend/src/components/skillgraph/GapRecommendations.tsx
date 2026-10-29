"use client";

import { SkillResult } from "@/lib/skillgraph-types";

interface GapRecommendationsProps {
  requiredSkills: SkillResult[];
  preferredSkills: SkillResult[];
}

export function GapRecommendations({
  requiredSkills,
  preferredSkills,
}: GapRecommendationsProps) {
  // Collect skills with recommendations, required-first
  const withRec = [
    ...requiredSkills.filter((s) => s.recommendation),
    ...preferredSkills.filter((s) => s.recommendation),
  ];

  if (withRec.length === 0) {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-900/40 dark:bg-emerald-950/20">
        <p className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">
          🎉 No gap recommendations
        </p>
        <p className="mt-1 text-xs text-emerald-700 dark:text-emerald-400">
          Strong evidence was found for all skills in this job description.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
        Gap Recommendations ({withRec.length})
      </h4>
      <ol className="space-y-2">
        {withRec.map((skill, i) => (
          <li
            key={skill.canonical_name}
            className="flex gap-3 rounded-xl border border-zinc-200 bg-white p-3 dark:border-zinc-700 dark:bg-zinc-900"
          >
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400">
              {i + 1}
            </span>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">
                  {skill.canonical_name}
                </span>
                <span className="text-xs text-zinc-400">
                  ({skill.evidence_tier === "none" ? "No evidence" : "Weak evidence"})
                </span>
              </div>
              <p className="mt-0.5 text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">
                {skill.recommendation}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

