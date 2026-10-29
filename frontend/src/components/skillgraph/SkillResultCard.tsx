"use client";

import { EvidenceItem, SkillResult } from "@/lib/skillgraph-types";
import { getTierBadgeClasses } from "@/lib/skillgraph-api";

interface SkillResultCardProps {
  skill: SkillResult;
  isRequired: boolean;
}

function EvidenceRow({ item }: { item: EvidenceItem }) {
  const kindIcon: Record<string, string> = {
    import: "📦",
    symbol: "⚙️",
    docstring: "📝",
  };

  return (
    <li className="flex flex-col gap-0.5 rounded-lg bg-zinc-50 p-2 text-xs dark:bg-zinc-800/60">
      <div className="flex items-center gap-1.5">
        <span className="text-base">{kindIcon[item.kind] ?? "•"}</span>
        <span className="font-mono font-semibold text-zinc-800 dark:text-zinc-200">
          {item.kind}
        </span>
        {item.file_path && (
          <span className="ml-auto font-mono text-zinc-500 dark:text-zinc-400">
            {item.file_path}
            {item.start_line != null && item.end_line != null
              ? `:${item.start_line}–${item.end_line}`
              : item.start_line != null
              ? `:${item.start_line}`
              : ""}
          </span>
        )}
      </div>
      <p className="text-zinc-600 dark:text-zinc-400">{item.detail}</p>
    </li>
  );
}

export function SkillResultCard({ skill, isRequired }: SkillResultCardProps) {
  const tier = getTierBadgeClasses(skill.evidence_tier);

  return (
    <div
      className={`rounded-xl border p-4 ${tier.border} bg-white shadow-sm dark:bg-zinc-900`}
    >
      {/* Header row */}
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-sm font-bold text-zinc-900 dark:text-zinc-100">
            {skill.canonical_name}
          </span>
          {skill.aliases_matched.length > 0 && (
            <span className="text-xs text-zinc-400 dark:text-zinc-500">
              ({skill.aliases_matched.join(", ")})
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              isRequired
                ? "bg-zinc-200 text-zinc-700 dark:bg-zinc-700 dark:text-zinc-300"
                : "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400"
            }`}
          >
            {isRequired ? "Required" : "Preferred"}
          </span>
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-semibold ${tier.bg} ${tier.text}`}
          >
            {tier.label}
          </span>
        </div>
      </div>

      {/* Explanation */}
      <p className="mt-2 text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">
        {skill.explanation}
      </p>

      {/* Evidence items */}
      {skill.evidence_items.length > 0 && (
        <div className="mt-3">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Evidence
          </p>
          <ul className="space-y-1.5">
            {skill.evidence_items.map((item, i) => (
              <EvidenceRow key={i} item={item} />
            ))}
          </ul>
        </div>
      )}

      {/* Recommendation */}
      {skill.recommendation && (
        <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-2.5 dark:border-amber-900/40 dark:bg-amber-950/30">
          <p className="mb-0.5 text-xs font-semibold text-amber-800 dark:text-amber-300">
            💡 Recommended next step
          </p>
          <p className="text-xs leading-relaxed text-amber-700 dark:text-amber-400">
            {skill.recommendation}
          </p>
        </div>
      )}
    </div>
  );
}

