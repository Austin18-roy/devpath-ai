# devpath-ai
Evidence-driven AI engineering and career intelligence platform

---

## Overview

DevPath AI is a 30-day AI/ML engineering project uniting two complementary systems:
1. **RepoMind**: Python codebase parsing using AST, NetworkX dependency graphs, and change-impact analysis.
2. **SkillGraph**: Evidence-based skill extraction from repository artifacts, matching against job descriptions, identifying skill gaps, and generating personalized portfolio growth recommendations.

---

## Architecture & Project Structure

The project is structured as a decoupled monorepo:

```text
devpath-ai/
├── backend/                  # FastAPI Python backend (Python 3.13)
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint, CORS configuration
│   │   ├── core/config.py    # Pydantic Settings & environment config
│   │   └── api/v1/health.py  # Health check endpoint (/api/v1/health)
│   ├── tests/
│   │   ├── conftest.py       # TestClient test fixtures
│   │   └── test_health.py    # Pytest health check & CORS verification
│   ├── requirements.txt      # Production dependencies
│   ├── requirements-dev.txt  # Development & test dependencies
│   ├── pytest.ini            # Pytest configuration
│   └── .env.example          # Backend environment variables template
│
└── frontend/                 # Next.js App Router (TypeScript + Tailwind CSS)
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx      # Dashboard landing with live health card
    │   │   ├── layout.tsx    # Root layout & metadata
    │   │   └── globals.css   # Tailwind styles
    │   ├── components/
    │   │   └── BackendStatusCard.tsx  # Dynamic health status card (loading, success, error)
    │   └── lib/
    │       └── api.ts        # Typed API client for FastAPI
    ├── tests/
    │   └── api.test.mjs      # Frontend unit tests using Node.js test runner
    └── .env.example          # Frontend environment variables template
```

---

## Quickstart Guide for MacBook M2

### Prerequisites

- **Python**: 3.13+ installed (`python3 --version`)
- **Node.js**: 20+ installed (`node -v`)
- **Git**: Installed (`git --version`)

---

### 1. Backend Setup (FastAPI)

1. Open a terminal and navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install development & backend dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```

4. Create your local environment file (optional, defaults are pre-configured):
   ```bash
   cp .env.example .env
   ```

5. Run the test suite:
   ```bash
   pytest
   ```

6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API Root: [http://localhost:8000/](http://localhost:8000/)
   - Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
   - Interactive Swagger Docs: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

---

### 2. Frontend Setup (Next.js)

1. Open a second terminal window and navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Install dependencies (if not already installed):
   ```bash
   npm install
   ```

3. Verify environment configuration:
   ```bash
   cp .env.example .env.local
   ```
   *(Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000`)*

4. Run the frontend unit tests:
   ```bash
   npm test
   ```

5. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   - Open [http://localhost:3000](http://localhost:3000) in your browser.
   - The dashboard card will query the backend and display live **Online** status.

---

## Milestone Progress

- [x] **Milestone 1**: Project skeleton, FastAPI `/api/v1/health` with CORS, Next.js frontend with live status indicator, automated test suites (pytest + node:test), macOS M2 developer setup.
- [x] **Milestone 2**: RepoMind AST Parser, module/class/function extraction, NetworkX dependency graph, and reverse-reachability change-impact analysis (`POST /api/v1/repomind/analyze` and `POST /api/v1/repomind/impact`).
- [x] **Milestone 3**: RepoMind interactive React Flow visualization (`@xyflow/react`), live codebase scanner with real API metrics, symbol inspector drawer, and visual change-impact blast-radius highlighting.
- [x] **Milestone 4**: SkillGraph job-description skill extraction & alias normalization, evidence matching against repository artifacts (imports, symbols, docstrings), 3-tier classification (strong/weak/none) with plain-English rationales, actionable gap recommendations, and interactive UI dashboard.
- [x] **Milestone 5**: Intelligent Skill Evidence & Career Roadmap — multi-pattern AST call extraction, evidence confidence scoring (`high`, `medium`, `low`), deterministic NetworkX skill relationship network, role-tailored career roadmap mini-projects (AI/ML, Generative AI, SDE) with verifiable deliverables, verified official learning resources, and reactive client-side progress tracking (`localStorage` with `useSyncExternalStore`).
- [ ] **Milestone 6**: End-to-end integration, sample demo repository, and final documentation polish.
