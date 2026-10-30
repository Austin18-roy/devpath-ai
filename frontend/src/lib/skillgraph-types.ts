/**
 * skillgraph-types.ts — TypeScript interfaces for the SkillGraph API.
 * Directly mirrors the backend Pydantic models in app/services/skillgraph/models.py.
 */

import { AnalysisResult } from "./repomind-types";

export type EvidenceTier = "strong" | "weak" | "none";
export type EvidenceConfidence = "high" | "medium" | "low";
export type TargetRole = "all" | "aiml_engineer" | "genai_engineer" | "sde";

export interface EvidenceItem {
  kind: "import" | "symbol" | "docstring" | "call";
  package: string | null;
  symbol_id: string | null;
  symbol_name: string | null;
  file_path: string | null;
  start_line: number | null;
  end_line: number | null;
  line_number: number | null;
  detail: string;
  confidence: EvidenceConfidence;
}

export interface LearningResourceModel {
  title: string;
  url: string;
  type: "official_docs" | "tutorial" | "course";
  free: boolean;
}

export interface RoadmapTask {
  task_id?: string;
  skill_name: string;
  title?: string;
  task_title?: string;
  objective?: string;
  description?: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "Beginner" | "Intermediate" | "Advanced";
  estimated_hours: number;
  completion_criteria: string[];
  deliverable: string;
  role_relevance?: string;
  target_role_relevance?: string;
  developed_skills?: string[];
  resources: LearningResourceModel[];
}

export interface SkillResult {
  canonical_name: string;
  aliases_matched: string[];
  evidence_tier: EvidenceTier;
  evidence_items: EvidenceItem[];
  explanation: string;
  recommendation: string | null;
  related_skills: string[];
  roadmap_task: RoadmapTask | null;
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
  target_role?: TargetRole | null;
}

export interface SkillMatchResponse {
  skills_required: SkillResult[];
  skills_preferred: SkillResult[];
  role_roadmap?: RoadmapTask[];
  summary: MatchSummary;
  disclaimer: string;
}
