"use client";

import { useState } from "react";
import { SkillResult } from "@/lib/skillgraph-types";
import { getTierBadgeClasses } from "@/lib/skillgraph-api";

interface SkillRelationshipViewProps {
  skills: SkillResult[];
}

export function SkillRelationshipView({ skills }: SkillRelationshipViewProps) {
  const [selectedSkillName, setSelectedSkillName] = useState<string | null>(
    skills.length > 0 ? skills[0].canonical_name : null
  );

  if (skills.length === 0) {
    return (
      <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-6 text-center dark:border-zinc-800 dark:bg-zinc-900">
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          No skills available to display relationship clusters.
        </p>
      </div>
    );
  }

  const selectedSkill =
    skills.find((s) => s.canonical_name === selectedSkillName) || skills[0];

  const tier = getTierBadgeClasses(selectedSkill.evidence_tier);

  return (
    <div className="space-y-6">
      {/* Introduction */}
      <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
          Deterministic Skill Ecosystem Network
        </h3>
        <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
          Explore how identified job skills relate to each other in practical engineering workflows. Click any skill chip below to inspect its ecosystem cluster, prerequisites, and complementary tools.
        </p>

        {/* Interactive Skill Selector Chips */}
        <div className="mt-4 flex flex-wrap gap-2">
          {skills.map((skill) => {
            const isSelected = skill.canonical_name === selectedSkill.canonical_name;
            const skillTier = getTierBadgeClasses(skill.evidence_tier);
            return (
              <button
                key={skill.canonical_name}
                onClick={() => setSelectedSkillName(skill.canonical_name)}
                className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
                  isSelected
                    ? "border-indigo-600 bg-indigo-50 text-indigo-700 shadow-sm dark:border-indigo-500 dark:bg-indigo-950/60 dark:text-indigo-300 ring-2 ring-indigo-500/20"
                    : "border-zinc-200 bg-zinc-50 text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
                }`}
              >
                <span className="font-mono">{skill.canonical_name}</span>
                <span
                  className={`h-2 w-2 rounded-full ${
                    skill.evidence_tier === "strong"
                      ? "bg-emerald-500"
                      : skill.evidence_tier === "weak"
                      ? "bg-amber-500"
                      : "bg-red-400"
                  }`}
                  title={skillTier.label}
                />
              </button>
            );
          })}
        </div>
      </div>

      {/* Focused Skill Detail & Ecosystem Cluster */}
      <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-100 pb-3 dark:border-zinc-800">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
              Selected Skill Focus
            </span>
            <div className="flex items-center gap-2 mt-0.5">
              <h4 className="font-mono text-base font-bold text-zinc-900 dark:text-zinc-100">
                {selectedSkill.canonical_name}
              </h4>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-semibold ${tier.bg} ${tier.text}`}
              >
                {tier.label}
              </span>
            </div>
          </div>
          <div className="text-right text-xs text-zinc-500 dark:text-zinc-400">
            {selectedSkill.evidence_items.length} code evidence item(s) found
          </div>
        </div>

        <p className="mt-3 text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">
          {selectedSkill.explanation}
        </p>

        {/* Connected Ecosystem Skills Cluster */}
        <div className="mt-5">
          <h5 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-3">
            Ecosystem Relationships & Complementary Tools
          </h5>

          {selectedSkill.related_skills.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {selectedSkill.related_skills.map((relSkillName) => {
                // Check if this related skill is also in the job description or repo
                const matchInJob = skills.find(
                  (s) => s.canonical_name.toLowerCase() === relSkillName.toLowerCase()
                );

                return (
                  <div
                    key={relSkillName}
                    className={`rounded-lg border p-3 text-xs transition-all ${
                      matchInJob
                        ? "border-indigo-200 bg-indigo-50/40 dark:border-indigo-900/50 dark:bg-indigo-950/20"
                        : "border-zinc-200 bg-zinc-50/50 dark:border-zinc-800 dark:bg-zinc-800/40"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-zinc-800 dark:text-zinc-200">
                        {relSkillName}
                      </span>
                      {matchInJob ? (
                        <span className="rounded bg-indigo-100 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                          In Job Description
                        </span>
                      ) : (
                        <span className="text-[10px] text-zinc-400 dark:text-zinc-500">
                          Domain Complement
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-[11px] text-zinc-500 dark:text-zinc-400">
                      {matchInJob
                        ? `Evidence status: ${matchInJob.evidence_tier}`
                        : "Recommended companion technology for full domain proficiency"}
                    </p>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-zinc-400 italic">
              No specific complementary skill clusters registered for this skill.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

