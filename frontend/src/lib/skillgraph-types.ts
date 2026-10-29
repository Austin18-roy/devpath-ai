/**
 * skillgraph-types.ts — TypeScript interfaces for the SkillGraph API.
 * Directly mirrors the backend Pydantic models in app/services/skillgraph/models.py.
 */

import { AnalysisResult } from "./repomind-types";

export type EvidenceTier = "strong" | "weak" | "none";

export interface EvidenceItem {
  kind: "import" | "symbol" | "docstring";
  package: string | null;
  symbol_id: string | null;
  symbol_name: string | null;
  file_path: string | null;
  start_line: number | null;
  end_line: number | null;
  line_number: number | null;
  detail: string;
}

export interface SkillResult {
  canonical_name: string;
  aliases_matched: string[];
  evidence_tier: EvidenceTier;
  evidence_items: EvidenceItem[];
  explanation: string;
  recommendation: string | null;
}

export interface MatchSummary {
  required_count: number;
  preferred_count: number;
  strong_evidence_count: number;
  weak_evidence_count: number;
  no_evidence_count: number;
  coverage_note: string;
}

export interface SkillMatchRequest {
  job_description: string;
  analysis_result?: AnalysisResult | null;
}

export interface SkillMatchResponse {
  skills_required: SkillResult[];
  skills_preferred: SkillResult[];
  summary: MatchSummary;
  disclaimer: string;
}

