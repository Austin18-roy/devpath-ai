import { BackendStatusCard } from "@/components/BackendStatusCard";
import { DevPathClient } from "@/components/DevPathClient";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-12 lg:px-8">
      {/* Header */}
      <header className="mb-8 flex flex-col gap-3 border-b border-zinc-200 pb-6 dark:border-zinc-800 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-zinc-950 dark:text-zinc-50">
              DevPath AI
            </h1>
            <span className="rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold text-indigo-800 dark:bg-indigo-950/70 dark:text-indigo-300">
              Milestone 4: SkillGraph
            </span>
          </div>
          <p className="mt-1 text-base text-zinc-600 dark:text-zinc-400">
            Evidence-driven AI engineering and career intelligence platform
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
          <span>MacBook M2 Environment</span>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex flex-col gap-8">
        {/* Real-time Health Card */}
        <section>
          <BackendStatusCard />
        </section>

        {/* RepoMind + SkillGraph (Milestones 3 & 4) — shared state via DevPathClient */}
        <DevPathClient />

        {/* Product Component Cards */}
        <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* RepoMind Card */}
          <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 font-mono text-sm font-bold text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400">
                  RM
                </span>
                <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                  1. RepoMind Engine
                </h3>
              </div>
              <span className="rounded-md bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                Milestones 2 & 3 Done
              </span>
            </div>

            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              Parses Python codebases with Python AST, generates NetworkX dependency graphs, and runs reverse-reachability change-impact analysis.
            </p>

            <ul className="mt-4 space-y-1.5 text-xs text-zinc-500 dark:text-zinc-400">
              <li className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-medium">
                ✓ AST Visitor for classes, functions & imports
              </li>
              <li className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-medium">
                ✓ NetworkX directed dependency graph (Caller ──▶ Callee)
              </li>
              <li className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-medium">
                ✓ Interactive React Flow canvas with impact blast-radius halos
              </li>
            </ul>
          </div>

          {/* SkillGraph Card */}
          <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 font-mono text-sm font-bold text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400">
                  SG
                </span>
                <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                  2. SkillGraph Engine
                </h3>
              </div>
              <span className="rounded-md bg-zinc-100 px-2 py-1 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
                Milestone 4
              </span>
            </div>

            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              Extracts verifiable skill evidence directly from RepoMind repository artifacts and matches them against target job descriptions.
            </p>

            <ul className="mt-4 space-y-1.5 text-xs text-zinc-500 dark:text-zinc-400">
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-zinc-400" />
                Evidence-based skill identification
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-zinc-400" />
                Local embeddings & similarity gap scoring
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-zinc-400" />
                Actionable portfolio recommendations
              </li>
            </ul>
          </div>
        </section>

        {/* Development Quick-Guide */}
        <section className="rounded-2xl border border-zinc-200 bg-zinc-100/70 p-6 dark:border-zinc-800 dark:bg-zinc-900/50">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
            MacBook M2 Local Development Commands
          </h3>
          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="rounded-xl bg-white p-4 font-mono text-xs shadow-sm dark:bg-zinc-950">
              <p className="font-sans font-semibold text-zinc-900 dark:text-zinc-100">
                1. Backend (FastAPI)
              </p>
              <pre className="mt-2 overflow-x-auto text-zinc-700 dark:text-zinc-300">
{`cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000`}
              </pre>
            </div>

            <div className="rounded-xl bg-white p-4 font-mono text-xs shadow-sm dark:bg-zinc-950">
              <p className="font-sans font-semibold text-zinc-900 dark:text-zinc-100">
                2. Frontend (Next.js)
              </p>
              <pre className="mt-2 overflow-x-auto text-zinc-700 dark:text-zinc-300">
{`cd frontend
npm run dev`}
              </pre>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
