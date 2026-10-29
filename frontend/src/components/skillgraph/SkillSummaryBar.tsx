"use client";

import { MatchSummary } from "@/lib/skillgraph-types";

interface SkillSummaryBarProps {
  summary: MatchSummary;
}

interface BadgeProps {
  count: number;
  label: string;
  colorClass: string;
}

function Badge({ count, label, colorClass }: BadgeProps) {
  return (
    <div
      className={`flex flex-col items-center rounded-xl border px-3 py-2 text-center ${colorClass}`}
    >
      <span className="text-xl font-bold tabular-nums">{count}</span>
      <span className="mt-0.5 text-xs font-medium">{label}</span>
    </div>
  );
}

export function SkillSummaryBar({ summary }: SkillSummaryBarProps) {
  return (
    <div className="space-y-3">
      {/* Skill counts */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
        <Badge
          count={summary.required_count}
          label="Required"
          colorClass="border-zinc-200 bg-zinc-50 text-zinc-700 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
        />
        <Badge
          count={summary.preferred_count}
          label="Preferred"
          colorClass="border-zinc-100 bg-zinc-50/70 text-zinc-500 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400"
        />
        <Badge
          count={summary.strong_evidence_count}
          label="Strong evidence"
          colorClass="border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300"
        />
        <Badge
          count={summary.weak_evidence_count}
          label="Weak evidence"
          colorClass="border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-300"
        />
        <Badge
          count={summary.no_evidence_count}
          label="No evidence"
          colorClass="border-red-200 bg-red-50 text-red-800 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"
        />
      </div>

      {/* Coverage note */}
      <p className="rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2 text-xs leading-relaxed text-zinc-500 dark:border-zinc-700 dark:bg-zinc-800/50 dark:text-zinc-400">
        <span className="mr-1 font-semibold">Note:</span>
        {summary.coverage_note}
      </p>
    </div>
  );
}

