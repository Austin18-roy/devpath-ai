/**
 * skillgraph-api.ts — Typed fetch client for the SkillGraph /match endpoint.
 * Follows the same pattern as api.ts (RepoMind).
 */

import { getApiBaseUrl } from "./api";
import { AnalysisResult } from "./repomind-types";
import {
  EvidenceConfidence,
  SkillMatchRequest,
  SkillMatchResponse,
  TargetRole,
} from "./skillgraph-types";

/**
 * Build a SkillMatchRequest payload.
 * Exported as a pure function so it can be unit-tested independently.
 */
export function buildSkillMatchPayload(
  jobDescription: string,
  analysisResult?: AnalysisResult | null,
  targetRole?: TargetRole | null
): SkillMatchRequest {
  return {
    job_description: jobDescription,
    analysis_result: analysisResult ?? null,
    target_role: targetRole ?? "all",
  };
}

/**
 * POST /api/v1/skillgraph/match
 * Matches job-description skills against an optional RepoMind analysis result.
 */
export async function matchJobSkills(
  request: SkillMatchRequest
): Promise<SkillMatchResponse> {
  const baseUrl = getApiBaseUrl();
  const targetUrl = `${baseUrl}/api/v1/skillgraph/match`;

  let response: Response;
  try {
    response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(request),
    });
  } catch (err: unknown) {
    if (err instanceof Error) {
      if (
        err.message.includes("Failed to fetch") ||
        err.message.includes("ECONNREFUSED")
      ) {
        throw new Error(
          `Unable to connect to backend at ${baseUrl}. Ensure the FastAPI server is running.`
        );
      }
      throw err;
    }
    throw new Error(
      "An unexpected error occurred while contacting the SkillGraph service."
    );
  }

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson?.detail) {
        errorDetail =
          typeof errorJson.detail === "string"
            ? errorJson.detail
            : JSON.stringify(errorJson.detail);
      }
    } catch {
      // Body was not JSON — keep the status-based message
    }
    throw new Error(`Skill matching failed: ${errorDetail}`);
  }

  return response.json() as Promise<SkillMatchResponse>;
}

/**
 * Returns the Tailwind CSS colour token for a given evidence tier badge.
 * Exported as a pure function for unit testing.
 */
export function getTierBadgeClasses(tier: string): {
  bg: string;
  text: string;
  border: string;
  label: string;
} {
  switch (tier) {
    case "strong":
      return {
        bg: "bg-emerald-100 dark:bg-emerald-950/60",
        text: "text-emerald-800 dark:text-emerald-300",
        border: "border-emerald-200 dark:border-emerald-800",
        label: "Strong evidence",
      };
    case "weak":
      return {
        bg: "bg-amber-100 dark:bg-amber-950/60",
        text: "text-amber-800 dark:text-amber-300",
        border: "border-amber-200 dark:border-amber-800",
        label: "Weak evidence",
      };
    default:
      return {
        bg: "bg-red-100 dark:bg-red-950/60",
        text: "text-red-800 dark:text-red-300",
        border: "border-red-200 dark:border-red-800",
        label: "No evidence",
      };
  }
}

/**
 * Returns badge styling tokens for an evidence item's confidence rating.
 */
export function getConfidenceBadgeClasses(confidence: EvidenceConfidence): {
  bg: string;
  text: string;
  label: string;
} {
  switch (confidence) {
    case "high":
      return {
        bg: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
        text: "text-emerald-700 dark:text-emerald-300",
        label: "High confidence",
      };
    case "medium":
      return {
        bg: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
        text: "text-amber-700 dark:text-amber-300",
        label: "Medium confidence",
      };
    case "low":
    default:
      return {
        bg: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400",
        text: "text-zinc-600 dark:text-zinc-400",
        label: "Low confidence",
      };
  }
}
