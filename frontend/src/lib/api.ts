/**
 * DevPath AI API Client
 * Centralized client for communicating with the FastAPI backend.
 */

import { AnalysisResult, ChangeImpactReport } from "./repomind-types";

export interface HealthResponse {
  status: string;
  service: string;
  environment: string;
  version: string;
  timestamp: string;
}

/**
 * Returns the base API URL configured via NEXT_PUBLIC_API_URL or defaults to localhost:8000.
 */
export function getApiBaseUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (envUrl && envUrl.trim().length > 0) {
    return envUrl.replace(/\/+$/, "");
  }
  return "http://localhost:8000";
}

/**
 * Helper to handle fetch errors consistently.
 */
async function handleResponse<T>(response: Response, actionDescription: string): Promise<T> {
  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson && errorJson.detail) {
        errorDetail = typeof errorJson.detail === "string" ? errorJson.detail : JSON.stringify(errorJson.detail);
      }
    } catch {
      // Body was not JSON
    }
    throw new Error(`${actionDescription} failed: ${errorDetail}`);
  }
  return response.json();
}

/**
 * Fetches the backend health endpoint.
 */
export async function checkBackendHealth(): Promise<HealthResponse> {
  const baseUrl = getApiBaseUrl();
  const targetUrl = `${baseUrl}/api/v1/health`;

  try {
    const response = await fetch(targetUrl, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      cache: "no-store",
    });

    return await handleResponse<HealthResponse>(response, "Health check");
  } catch (err: unknown) {
    if (err instanceof Error) {
      if (err.message.includes("Failed to fetch") || err.message.includes("ECONNREFUSED")) {
        throw new Error(
          `Unable to connect to backend at ${baseUrl}. Ensure the FastAPI server is running.`
        );
      }
      throw err;
    }
    throw new Error("An unexpected error occurred while contacting the backend.");
  }
}

/**
 * Analyzes a Python repository using the RepoMind AST parser.
 */
export async function analyzeRepository(repoPath: string): Promise<AnalysisResult> {
  const baseUrl = getApiBaseUrl();
  const targetUrl = `${baseUrl}/api/v1/repomind/analyze`;

  try {
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ repo_path: repoPath }),
    });

    return await handleResponse<AnalysisResult>(response, "Repository scan");
  } catch (err: unknown) {
    if (err instanceof Error) {
      if (err.message.includes("Failed to fetch") || err.message.includes("ECONNREFUSED")) {
        throw new Error(
          `Unable to connect to backend at ${baseUrl}. Ensure FastAPI is running on port 8000.`
        );
      }
      throw err;
    }
    throw new Error("An unexpected error occurred during repository analysis.");
  }
}

/**
 * Evaluates potential change impact for a symbol using reverse reachability.
 */
export async function analyzeChangeImpact(repoPath: string, symbolId: string): Promise<ChangeImpactReport> {
  const baseUrl = getApiBaseUrl();
  const targetUrl = `${baseUrl}/api/v1/repomind/impact`;

  try {
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ repo_path: repoPath, symbol_id: symbolId }),
    });

    return await handleResponse<ChangeImpactReport>(response, "Change impact analysis");
  } catch (err: unknown) {
    if (err instanceof Error) {
      if (err.message.includes("Failed to fetch") || err.message.includes("ECONNREFUSED")) {
        throw new Error(
          `Unable to connect to backend at ${baseUrl}. Ensure FastAPI is running on port 8000.`
        );
      }
      throw err;
    }
    throw new Error("An unexpected error occurred during change impact analysis.");
  }
}
