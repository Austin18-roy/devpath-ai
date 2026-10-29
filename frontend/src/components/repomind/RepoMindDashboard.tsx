"use client";

import { useState, useMemo, useCallback } from "react";
import { analyzeRepository, analyzeChangeImpact } from "@/lib/api";
import { AnalysisResult, ChangeImpactReport, CodeSymbol } from "@/lib/repomind-types";
import { symbolsAndEdgesToGraph } from "@/lib/graph-adapter";
import { RepoScanner } from "./RepoScanner";
import { RepoMindGraphView } from "./RepoMindGraphView";
import { SymbolDetailsDrawer } from "./SymbolDetailsDrawer";

interface RepoMindDashboardProps {
  /** Optional callback invoked whenever a scan completes (or is cleared).
   *  Used by the parent DevPathClient to share the result with SkillGraph. */
  onAnalysisResult?: (result: AnalysisResult | null) => void;
}

export function RepoMindDashboard({ onAnalysisResult }: RepoMindDashboardProps = {}) {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [impactReport, setImpactReport] = useState<ChangeImpactReport | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState<CodeSymbol | null>(null);
  const [currentRepoPath, setCurrentRepoPath] = useState<string>("backend/tests/fixtures/sample_repo");

  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzingImpact, setIsAnalyzingImpact] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [impactError, setImpactError] = useState<string | null>(null);

  const handleAnalyze = useCallback(async (path: string) => {
    setIsLoading(true);
    setError(null);
    setImpactError(null);
    setImpactReport(null);
    setCurrentRepoPath(path);

    try {
      const result = await analyzeRepository(path);
      setAnalysisResult(result);
      onAnalysisResult?.(result);
      // Auto-select multiply if present, or first function/method for immediate inspection
      const multiplySym = result.symbols.find((s) => s.name === "multiply" && s.symbol_type === "function");
      const firstFunc = result.symbols.find((s) => s.symbol_type === "function" || s.symbol_type === "method");
      setSelectedSymbol(multiplySym || firstFunc || result.symbols[0] || null);
    } catch (err) {
      setAnalysisResult(null);
      onAnalysisResult?.(null);
      setSelectedSymbol(null);
      setError(err instanceof Error ? err.message : "Failed to analyze repository");
    } finally {
      setIsLoading(false);
    }
  }, [onAnalysisResult]);

  const handleAnalyzeImpact = useCallback(async (symbolId: string) => {
    // Prefer the canonical repo_path returned by the backend scan
    const pathForImpact = analysisResult?.repo_path || currentRepoPath;
    if (!pathForImpact) return;
    setIsAnalyzingImpact(true);
    setImpactError(null);

    try {
      const report = await analyzeChangeImpact(pathForImpact, symbolId);
      setImpactReport(report);
    } catch (err) {
      setImpactError(err instanceof Error ? err.message : "Failed to evaluate change impact");
    } finally {
      setIsAnalyzingImpact(false);
    }
  }, [analysisResult, currentRepoPath]);

  const handleSelectSymbol = useCallback((symbol: CodeSymbol) => {
    setSelectedSymbol(symbol);
    setImpactError(null);
  }, []);

  const handleSelectSymbolById = useCallback((symbolId: string) => {
    if (!analysisResult) return;
    const target = analysisResult.symbols.find((s) => s.id === symbolId);
    if (target) {
      setSelectedSymbol(target);
      setImpactError(null);
    }
  }, [analysisResult]);

  const handleClearImpact = useCallback(() => {
    setImpactReport(null);
    setImpactError(null);
  }, []);

  // Compute React Flow nodes and edges purely via adapter
  const { nodes, edges } = useMemo(() => {
    if (!analysisResult) return { nodes: [], edges: [] };
    return symbolsAndEdgesToGraph(
      analysisResult.symbols,
      analysisResult.edges,
      impactReport,
      selectedSymbol?.id || null
    );
  }, [analysisResult, impactReport, selectedSymbol]);

  return (
    <div className="flex flex-col gap-6">
      {/* 1. Repository Input & Diagnostic Bar */}
      <RepoScanner
        onAnalyze={handleAnalyze}
        isLoading={isLoading}
        result={analysisResult}
        error={error}
      />

      {/* 2. Interactive Canvas & Inspector Split Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left: React Flow Visualizer (2 Cols) */}
        <div className="lg:col-span-2">
          <RepoMindGraphView
            nodes={nodes}
            edges={edges}
            isLoading={isLoading}
            onSelectSymbol={handleSelectSymbol}
            selectedSymbolId={selectedSymbol?.id || null}
          />
        </div>

        {/* Right: Symbol Details & Change Impact Drawer (1 Col) */}
        <div className="lg:col-span-1">
          <SymbolDetailsDrawer
            symbol={selectedSymbol}
            edges={analysisResult?.edges || []}
            allSymbols={analysisResult?.symbols || []}
            onAnalyzeImpact={handleAnalyzeImpact}
            isAnalyzingImpact={isAnalyzingImpact}
            impactReport={impactReport}
            impactError={impactError}
            onClearImpact={handleClearImpact}
            onSelectSymbolById={handleSelectSymbolById}
          />
        </div>
      </div>
    </div>
  );
}
