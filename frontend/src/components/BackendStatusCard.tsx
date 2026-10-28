"use client";

import { useEffect, useState, useCallback } from "react";
import { checkBackendHealth, getApiBaseUrl, HealthResponse } from "@/lib/api";

type StatusState = "loading" | "connected" | "error";

export function BackendStatusCard() {
  const [state, setState] = useState<StatusState>("loading");
  const [data, setData] = useState<HealthResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const performHealthCheck = useCallback(async () => {
    setIsRefreshing(true);
    setErrorMessage(null);

    try {
      const response = await checkBackendHealth();
      setData(response);
      setState("connected");
      setLastChecked(new Date().toLocaleTimeString());
    } catch (err) {
      setData(null);
      setState("error");
      setErrorMessage(
        err instanceof Error ? err.message : "Failed to connect to backend service"
      );
      setLastChecked(new Date().toLocaleTimeString());
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    let ignore = false;

    // Asynchronous initial fetch without synchronous pre-await setState
    checkBackendHealth()
      .then((response) => {
        if (!ignore) {
          setData(response);
          setState("connected");
          setLastChecked(new Date().toLocaleTimeString());
        }
      })
      .catch((err) => {
        if (!ignore) {
          setData(null);
          setState("error");
          setErrorMessage(
            err instanceof Error ? err.message : "Failed to connect to backend service"
          );
          setLastChecked(new Date().toLocaleTimeString());
        }
      });

    return () => {
      ignore = true;
    };
  }, []);

  const apiUrl = getApiBaseUrl();

  return (
    <div className="w-full rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              Backend Service Status
            </h2>
            {state === "loading" && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-950/50 dark:text-amber-300">
                <span className="h-2 w-2 animate-pulse rounded-full bg-amber-500" />
                Connecting...
              </span>
            )}
            {state === "connected" && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                Online
              </span>
            )}
            {state === "error" && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-medium text-rose-700 dark:bg-rose-950/50 dark:text-rose-300">
                <span className="h-2 w-2 rounded-full bg-rose-500" />
                Offline
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            Target Endpoint: <code className="rounded bg-zinc-100 px-1 py-0.5 font-mono text-xs dark:bg-zinc-800">{apiUrl}/api/v1/health</code>
          </p>
        </div>

        <button
          onClick={performHealthCheck}
          disabled={isRefreshing || state === "loading"}
          className="inline-flex items-center justify-center rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-700 shadow-sm transition hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-200 dark:hover:bg-zinc-750"
        >
          {isRefreshing ? "Checking..." : "Re-check Health"}
        </button>
      </div>

      {/* State: Loading */}
      {state === "loading" && (
        <div className="mt-6 animate-pulse space-y-3 rounded-xl bg-zinc-50 p-5 dark:bg-zinc-800/40">
          <div className="h-4 w-1/3 rounded bg-zinc-200 dark:bg-zinc-700" />
          <div className="h-4 w-2/3 rounded bg-zinc-200 dark:bg-zinc-700" />
          <div className="h-4 w-1/2 rounded bg-zinc-200 dark:bg-zinc-700" />
        </div>
      )}

      {/* State: Connected */}
      {state === "connected" && data && (
        <div className="mt-6 space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-zinc-100 bg-zinc-50 p-4 dark:border-zinc-800/60 dark:bg-zinc-800/30">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Service</span>
              <p className="mt-1 font-mono text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                {data.service}
              </p>
            </div>
            <div className="rounded-xl border border-zinc-100 bg-zinc-50 p-4 dark:border-zinc-800/60 dark:bg-zinc-800/30">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Status</span>
              <p className="mt-1 font-mono text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                {data.status.toUpperCase()}
              </p>
            </div>
            <div className="rounded-xl border border-zinc-100 bg-zinc-50 p-4 dark:border-zinc-800/60 dark:bg-zinc-800/30">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Environment</span>
              <p className="mt-1 font-mono text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                {data.environment}
              </p>
            </div>
            <div className="rounded-xl border border-zinc-100 bg-zinc-50 p-4 dark:border-zinc-800/60 dark:bg-zinc-800/30">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">API Version</span>
              <p className="mt-1 font-mono text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                v{data.version}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
            <span>Server Timestamp: <code className="font-mono">{data.timestamp}</code></span>
            {lastChecked && <span>Last verified locally at {lastChecked}</span>}
          </div>
        </div>
      )}

      {/* State: Error */}
      {state === "error" && (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50/60 p-5 dark:border-rose-900/60 dark:bg-rose-950/20">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 rounded-full bg-rose-100 p-1 text-rose-600 dark:bg-rose-900 dark:text-rose-300">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-rose-800 dark:text-rose-200">
                Connection Failed
              </h3>
              <p className="mt-1 text-sm text-rose-700 dark:text-rose-300">
                {errorMessage}
              </p>
              <div className="mt-4 rounded-lg bg-white/70 p-3 text-xs text-zinc-700 shadow-sm dark:bg-zinc-900/70 dark:text-zinc-300">
                <p className="font-medium">Troubleshooting for your MacBook M2:</p>
                <ol className="mt-1 list-inside list-decimal space-y-1">
                  <li>Open a terminal in <code className="font-mono bg-zinc-100 dark:bg-zinc-800 px-1 py-0.5 rounded">backend/</code></li>
                  <li>Activate the virtual environment: <code className="font-mono bg-zinc-100 dark:bg-zinc-800 px-1 py-0.5 rounded">source .venv/bin/activate</code></li>
                  <li>Start the server: <code className="font-mono bg-zinc-100 dark:bg-zinc-800 px-1 py-0.5 rounded">uvicorn app.main:app --reload --port 8000</code></li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
