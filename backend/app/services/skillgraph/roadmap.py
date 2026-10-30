"""
roadmap.py — Personalized, practical career roadmap generator for DevPath AI.

Design principles:
- Genuinely role-tailored mini-projects for AI/ML Engineer, Generative AI Engineer, and SDE.
- Tailored for beginners / second-year AIML students.
- Generates actionable, realistic mini-projects (1–3 hours) rather than vague advice.
- Each task includes clear objectives, measurable completion criteria, portfolio deliverable,
  estimated hours, difficulty rating, role relevance, and verified free learning resources.
- Zero employment or hiring outcome claims.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from app.services.skillgraph.resources import get_learning_resources


@dataclass
class RoadmapTaskData:
    """Actionable mini-project roadmap task for a specific skill gap."""
    task_id: str
    skill_name: str
    title: str
    difficulty: str  # "Beginner" | "Intermediate" | "Advanced"
    estimated_hours: int
    role_relevance: Dict[str, str]  # Role key -> why it matters explanation
    objective: str                   # What the learner should accomplish
    description: str                 # Technical implementation details
    deliverable: str
    completion_criteria: List[str]
    developed_skills: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Role-Specific Curated Mini-Projects
# ---------------------------------------------------------------------------

AIML_ENGINEER_TASKS: List[RoadmapTaskData] = [
    RoadmapTaskData(
        task_id="task-aiml-numpy-01",
        skill_name="numpy",
        title="NumPy Numerical Computing and Regression",
        difficulty="Beginner",
        estimated_hours=2,
        role_relevance={
            "all": "Builds the foundational mathematical proficiency required for numerical array processing and machine learning algorithms.",
            "aiml_engineer": "Directly powers custom loss functions, matrix transformations, gradient calculations, and numerical stability in ML models.",
            "genai_engineer": "Essential for manipulating embedding tensors, computing cosine similarities, and processing multi-dimensional attention matrices.",
            "sde": "Demonstrates how to optimize memory layout and perform high-speed in-memory vector computations without slow Python loops.",
        },
        objective="Implement ordinary least squares linear regression from scratch using vectorized NumPy matrix operations (normal equation) to predict continuous targets without high-level ML frameworks.",
        description=(
            "Implement vectorized numerical array operations and ordinary least squares linear regression "
            "from scratch using pure NumPy matrix math (normal equation: (X^T X)^-1 X^T y) without using high-level ML wrappers."
        ),
        deliverable="A runnable Python script `matrix_regression.py` calculating regression weights and RMSE on synthetic or benchmark data.",
        completion_criteria=[
            "Construct design matrix X with an added bias column and target vector y",
            "Calculate parameter weights using the normal equation np.linalg.pinv(X.T @ X) @ X.T @ y",
            "Implement vectorized prediction function without explicit Python for-loops",
            "Calculate and print Root Mean Squared Error (RMSE) using np.sqrt and np.mean",
        ],
        developed_skills=["python", "scipy", "math"],
    ),
    RoadmapTaskData(
        task_id="task-aiml-pandas-02",
        skill_name="pandas",
        title="pandas Data Cleaning and Analysis",
        difficulty="Beginner",
        estimated_hours=2,
        role_relevance={
            "all": "Provides standard tabular data wrangling, missing-value imputation, and multi-column aggregation capabilities.",
            "aiml_engineer": "Foundational for preparing clean training datasets, handling real-world sensor/business data irregularities, and feature engineering.",
            "genai_engineer": "Used to clean unstructured text corpora, format fine-tuning datasets, and organize model evaluation logs.",
            "sde": "Standard utility for ETL data parsing, structured data transformations, CSV/Parquet conversions, and analytics reporting.",
        },
        objective="Build an automated data cleaning and exploratory analysis pipeline that detects null values, imputes missing features, computes statistical aggregations, and exports optimized Parquet data.",
        description=(
            "Build a reproducible data preprocessing and exploratory analysis pipeline that ingests raw tabular data, "
            "handles missing values, computes multi-column statistical aggregations, and exports clean Parquet output."
        ),
        deliverable="Python script `clean_data.py` producing an aggregated metrics report and cleaned dataset output.",
        completion_criteria=[
            "Load tabular data with explicit column dtypes and parse dates",
            "Detect missing values and perform strategic imputation or filtering",
            "Perform multi-column groupby operations with summary statistics (mean, median, std)",
            "Export cleaned dataset to compressed Parquet format",
        ],
        developed_skills=["numpy", "python"],
    ),
    RoadmapTaskData(
        task_id="task-aiml-sklearn-03",
        skill_name="scikit-learn",
        title="scikit-learn Machine Learning Pipeline",
        difficulty="Beginner",
        estimated_hours=2,
        role_relevance={
            "all": "The industry standard framework for classical machine learning, feature transformers, and model evaluation.",
            "aiml_engineer": "Essential for building robust baselines, preventing data leakage with Pipelines, tuning hyperparameters, and deploying production models.",
            "genai_engineer": "Widely used for post-processing model embeddings, training lightweight classifier heads, and clustering latent vectors.",
            "sde": "Demonstrates how to design reproducible prediction workflows and package ML models with standardized transform and predict interfaces.",
        },
        objective="Construct an end-to-end scikit-learn Pipeline combining feature scaling (StandardScaler), an estimator (RandomForestClassifier or LogisticRegression), and 5-fold cross-validation.",
        description=(
            "Construct an end-to-end scikit-learn Pipeline combining feature scaling (StandardScaler), "
            "an estimator (LogisticRegression or RandomForestClassifier), and 5-fold cross-validation."
        ),
        deliverable="A script `ml_pipeline.py` training a model and reporting cross-validation precision, recall, and F1 scores.",
        completion_criteria=[
            "Split dataset into train and test sets using train_test_split with stratified sampling",
            "Build a scikit-learn Pipeline combining StandardScaler and an estimator",
            "Evaluate model performance using cross_val_score across 5 folds",
            "Generate and display classification_report and confusion matrix",
        ],
        developed_skills=["pandas", "numpy", "python"],
    ),
    RoadmapTaskData(
        task_id="task-aiml-eval-04",
        skill_name="model-evaluation",
        title="Model Evaluation and Validation",
        difficulty="Intermediate",
        estimated_hours=2,
        role_relevance={
            "all": "Rigorous quantitative assessment of predictive performance, error distribution, and model reliability.",
            "aiml_engineer": "Crucial for identifying class imbalance issues, measuring precision-recall trade-offs, preventing overfitting, and validating generalization.",
            "genai_engineer": "Provides the essential statistical methodology for designing automated LLM benchmark scoring and error rate tracking.",
            "sde": "Applies rigorous test-driven validation standards to verify that production algorithms meet quality thresholds.",
        },
        objective="Develop a comprehensive diagnostic evaluation script computing confusion matrices, ROC-AUC curves, precision-recall trade-offs, and residual error distributions.",
        description=(
            "Implement a comprehensive model diagnostics suite computing precision-recall trade-offs, "
            "ROC-AUC curves, confusion matrices, and calibration checks across validation splits."
        ),
        deliverable="Diagnostic script `model_evaluation.py` outputting validation metrics, ROC-AUC score, and error trade-offs.",
        completion_criteria=[
            "Compute confusion matrix, precision, recall, and F1-score across validation splits",
            "Generate ROC curve data points and calculate ROC-AUC score using sklearn.metrics",
            "Analyze prediction error distributions and false positive vs false negative trade-offs",
            "Document model performance thresholds and recommendations in script comments",
        ],
        developed_skills=["scikit-learn", "numpy", "matplotlib"],
    ),
]

GENAI_ENGINEER_TASKS: List[RoadmapTaskData] = [
    RoadmapTaskData(
        task_id="task-genai-llm-api-01",
        skill_name="llm-api",
        title="LLM API Integration",
        difficulty="Beginner",
        estimated_hours=2,
        role_relevance={
            "all": "Core interface for connecting applications to state-of-the-art foundation models and hosted inference endpoints.",
            "aiml_engineer": "Bridges custom internal models with hosted foundation model APIs to create hybrid intelligent systems.",
            "genai_engineer": "Fundamental competency for prompt engineering, token streaming, rate-limit retry management, and schema-constrained JSON outputs.",
            "sde": "Demonstrates integration of external AI service SDKs, asynchronous HTTP clients, and rigorous response validation.",
        },
        objective="Build a resilient Python client that interfaces with an LLM API (Gemini or OpenAI), enforces Pydantic schema validation for structured outputs, and handles rate limits with exponential backoff.",
        description=(
            "Connect to a modern LLM API (e.g. Gemini, OpenAI, or local Ollama) with temperature control, "
            "structured prompts, and Pydantic schema validation for guaranteed typed JSON outputs."
        ),
        deliverable="Script `llm_client.py` executing structured prompt requests with exponential backoff and schema validation.",
        completion_criteria=[
            "Configure API client with environment-variable credential management",
            "Implement system prompt guiding the model to adhere to a strict response schema",
            "Enforce JSON output matching a Pydantic model with validation error handling",
            "Implement exponential backoff or retry handling for rate limits",
        ],
        developed_skills=["python", "pydantic", "fastapi"],
    ),
    RoadmapTaskData(
        task_id="task-genai-embeddings-02",
        skill_name="embeddings",
        title="Embeddings and Semantic Search",
        difficulty="Intermediate",
        estimated_hours=2,
        role_relevance={
            "all": "Converts unstructured human language into mathematical vector spaces for semantic comparison and retrieval.",
            "aiml_engineer": "Bridges representation learning, dimensional reduction, and nearest-neighbor vector search algorithms.",
            "genai_engineer": "The core building block for retrieval-augmented generation (RAG), semantic document deduplication, and contextual routing.",
            "sde": "Demonstrates how to integrate high-dimensional vector representations and similarity metrics into data querying layers.",
        },
        objective="Generate dense vector embeddings from a text corpus using a local Sentence-Transformers model and implement cosine similarity search to retrieve top-ranked passages for queries.",
        description=(
            "Generate dense text embeddings using a local sentence-transformers model (e.g. all-MiniLM-L6-v2) "
            "and implement cosine similarity search to retrieve top-K ranked text chunks for user queries."
        ),
        deliverable="Python script `semantic_search.py` indexing document chunks and returning ranked search results with scores.",
        completion_criteria=[
            "Load local embedding model (e.g. all-MiniLM-L6-v2) without external paid API dependencies",
            "Encode a corpus of text passages into normalized vector embeddings",
            "Compute cosine similarity matrix between query embedding and corpus embeddings",
            "Return top-K ranked documents with relevance similarity scores",
        ],
        developed_skills=["sentence-transformers", "numpy", "chromadb"],
    ),
    RoadmapTaskData(
        task_id="task-genai-rag-03",
        skill_name="langchain",
        title="Retrieval-Augmented Generation (RAG)",
        difficulty="Intermediate",
        estimated_hours=3,
        role_relevance={
            "all": "The leading architecture for grounding generative models in verified private documents and reducing hallucinations.",
            "aiml_engineer": "Integrates information retrieval pipelines with generative language models for domain-specific question answering.",
            "genai_engineer": "Non-negotiable core competency for building enterprise generative AI systems, private knowledge assistants, and search engines.",
            "sde": "Demonstrates how to architect end-to-end data ingestion pipelines, vector stores, and contextual prompt construction.",
        },
        objective="Construct a modular RAG pipeline that chunks source documents with overlap, indexes vectors in a local ChromaDB store, and synthesizes grounded answers citing retrieved source chunks.",
        description=(
            "Create a modular RAG pipeline that reads text files, chunks documents with overlap, "
            "indexes vectors in a local ChromaDB store, and synthesizes answers using retrieved context."
        ),
        deliverable="Runnable script `rag_pipeline.py` accepting questions and answering strictly from ingested context.",
        completion_criteria=[
            "Chunk source documents using recursive character splitting with overlap",
            "Index chunk embeddings into local vector store (ChromaDB or FAISS)",
            "Retrieve top-3 relevant context chunks for incoming user queries",
            "Synthesize answer using prompt template that cites retrieved source chunks",
        ],
        developed_skills=["chromadb", "python", "generative-ai"],
    ),
    RoadmapTaskData(
        task_id="task-genai-eval-04",
        skill_name="generative-ai",
        title="Build a Small LLM Application with Evaluation",
        difficulty="Intermediate",
        estimated_hours=3,
        role_relevance={
            "all": "End-to-end application lifecycle management and automated quality benchmarking for generative systems.",
            "aiml_engineer": "Establishes quantitative benchmarks to track performance regressions, prompt variations, and fine-tuning improvements.",
            "genai_engineer": "Critical portfolio project proving you can deliver an actual working generative AI application paired with measurable quality validation.",
            "sde": "Applies automated testing, assertion suites, and guardrails to stochastic language model application outputs.",
        },
        objective="Build a complete mini generative application (e.g. document summarizer or structured extractor) paired with an automated evaluation benchmark scoring answer faithfulness and prompt compliance.",
        description=(
            "Build an end-to-end mini LLM application (e.g. text summarizer or code explainer) paired with an automated "
            "evaluation harness measuring faithfulness, prompt compliance, and hallucination checks."
        ),
        deliverable="Project folder `llm_app/` with application logic `app.py` and evaluation harness `evaluate.py`.",
        completion_criteria=[
            "Build functional LLM application solving a concrete task (e.g. summarization or extraction)",
            "Define test dataset of 5+ input prompts with expected reference outputs or criteria",
            "Implement evaluation harness checking exact matches, keyword presence, or LLM-as-a-judge score",
            "Log evaluation results and hallucination checks to a summary report",
        ],
        developed_skills=["langchain", "pytest", "python"],
    ),
]

SDE_TASKS: List[RoadmapTaskData] = [
    RoadmapTaskData(
        task_id="task-sde-git-01",
        skill_name="git",
        title="Git and Collaborative Development Workflow",
        difficulty="Beginner",
        estimated_hours=1,
        role_relevance={
            "all": "Universal source control system for tracking changes, authoring conventional commits, and collaborating in teams.",
            "aiml_engineer": "Essential for versioning ML experiment scripts, model configs, pipeline definitions, and data contracts.",
            "genai_engineer": "Crucial for versioning prompt templates, evaluation benchmarks, agent configs, and tool definitions.",
            "sde": "Non-negotiable day-one foundation for trunk-based development, peer code reviews, release branching, and merge conflict resolution.",
        },
        objective="Establish a professional Git workflow by creating feature branches, authoring atomic conventional commits (feat:, fix:, test:), authoring a PR template, and performing a clean rebase and merge.",
        description=(
            "Demonstrate clean Git hygiene: create a feature branch, author conventional atomic commits, "
            "and craft a descriptive Pull Request template in your repository."
        ),
        deliverable="Git commit history in repository with `.github/pull_request_template.md`.",
        completion_criteria=[
            "Feature branch created from main with clear naming convention (e.g. feature/add-endpoint)",
            "3+ atomic commits authored adhering to Conventional Commits standard (feat:, fix:, test:)",
            "Pull request template created standardizing description, checklist, and verification notes",
            "Branch successfully rebased and merged cleanly without merge commits",
        ],
        developed_skills=["software-engineering", "cloud-devops"],
    ),
    RoadmapTaskData(
        task_id="task-sde-fastapi-02",
        skill_name="fastapi",
        title="REST API Development and Validation",
        difficulty="Beginner",
        estimated_hours=2,
        role_relevance={
            "all": "Modern asynchronous Python web framework for building high-throughput microservices and APIs.",
            "aiml_engineer": "Standard framework for serving trained machine learning models as production REST inference services.",
            "genai_engineer": "The primary framework for serving streaming completions, agent endpoints, and RAG search backends.",
            "sde": "Core software development competency: RESTful design, Pydantic input/output schemas, HTTP status codes, and OpenAPI documentation.",
        },
        objective="Develop a structured REST API using FastAPI featuring CRUD endpoints, request/response Pydantic models, custom exception handlers, and automated test coverage with TestClient.",
        description=(
            "Develop a type-safe REST API using FastAPI featuring CRUD endpoints, request/response Pydantic models, "
            "custom exception handlers, and automated testing with TestClient."
        ),
        deliverable="FastAPI service module `app/main.py` and automated API tests `tests/test_api.py`.",
        completion_criteria=[
            "Implement GET, POST, PUT, DELETE endpoints with appropriate HTTP status codes (200, 201, 404, 422)",
            "Validate all request bodies and query parameters with Pydantic schemas",
            "Implement central exception handler returning structured JSON error payloads",
            "Automate test coverage for all endpoints using TestClient",
        ],
        developed_skills=["pydantic", "pytest", "python"],
    ),
    RoadmapTaskData(
        task_id="task-sde-db-03",
        skill_name="postgresql",
        title="Database Integration and CRUD Operations",
        difficulty="Intermediate",
        estimated_hours=2,
        role_relevance={
            "all": "Reliable data persistence using ACID-compliant relational databases, SQL queries, and ORM abstractions.",
            "aiml_engineer": "Stores training run metadata, model registry artifacts, feature stores, and prediction logs.",
            "genai_engineer": "Commonly paired with pgvector to combine relational business data with high-dimensional vector embeddings.",
            "sde": "Essential backend engineering foundation: normalized relational schemas, foreign key constraints, parameterized queries, and transactional integrity.",
        },
        objective="Implement data persistence using SQLAlchemy or psycopg with normalized relational tables, foreign key relationships, parameterized queries, and ACID transactions.",
        description=(
            "Implement database persistence using SQLAlchemy or psycopg with relational tables, foreign keys, "
            "transactions, parameterized queries, and CRUD helper routines."
        ),
        deliverable="Database layer module `database.py` with entity models and CRUD helper functions.",
        completion_criteria=[
            "Define relational schema with primary keys, foreign key constraints, and timestamps",
            "Implement CRUD functions with session management and transaction commit/rollback",
            "Use parameterized queries or ORM expressions preventing SQL injection vulnerabilities",
            "Write test script verifying record creation, relation querying, and cascade deletion",
        ],
        developed_skills=["sql", "sqlalchemy", "python"],
    ),
    RoadmapTaskData(
        task_id="task-sde-test-04",
        skill_name="pytest",
        title="Automated Testing and Software Quality",
        difficulty="Beginner",
        estimated_hours=2,
        role_relevance={
            "all": "The industry standard Python testing framework for ensuring software reliability, correctness, and preventing regressions.",
            "aiml_engineer": "Guards against silent data corruption, invalid tensor dimensions, and metric calculation regressions.",
            "genai_engineer": "Essential for automated evaluation harnesses, prompt assertions, and output guardrail validation.",
            "sde": "Core software craftsmanship: unit testing, table-driven tests with parameterization, dependency mocking, and test coverage.",
        },
        objective="Author a comprehensive pytest suite featuring reusable fixtures, parameterized table-driven test cases, and dependency mocking to verify application logic with zero failures.",
        description=(
            "Write a comprehensive pytest suite for core application logic featuring modular fixtures, "
            "table-driven tests using `@pytest.mark.parametrize`, and dependency mocking."
        ),
        deliverable="Test directory `tests/` with modular test files that run and pass cleanly with `pytest -v`.",
        completion_criteria=[
            "Create modular pytest fixtures for reusable test state and teardown",
            "Use @pytest.mark.parametrize to test boundary values and edge cases",
            "Mock external network or database calls using unittest.mock or pytest-mock",
            "Achieve clean passing test suite verifying core business logic with zero failures",
        ],
        developed_skills=["python", "software-engineering"],
    ),
]

ALL_ROLES_TASKS: List[RoadmapTaskData] = [
    SDE_TASKS[0],           # Git and Collaborative Development Workflow
    AIML_ENGINEER_TASKS[0], # NumPy Numerical Computing and Regression
    SDE_TASKS[1],           # REST API Development and Validation
    GENAI_ENGINEER_TASKS[2], # Retrieval-Augmented Generation (RAG)
]

ROLE_ROADMAPS: Dict[str, List[RoadmapTaskData]] = {
    "aiml_engineer": AIML_ENGINEER_TASKS,
    "genai_engineer": GENAI_ENGINEER_TASKS,
    "sde": SDE_TASKS,
    "all": ALL_ROLES_TASKS,
}


# ---------------------------------------------------------------------------
# Template Map for Skill-Lookup Fallback
# ---------------------------------------------------------------------------

ROADMAP_TEMPLATES: Dict[str, RoadmapTaskData] = {
    t.skill_name: t
    for task_list in (AIML_ENGINEER_TASKS, GENAI_ENGINEER_TASKS, SDE_TASKS)
    for t in task_list
}
# Additional canonical skills
ROADMAP_TEMPLATES["pytorch"] = RoadmapTaskData(
    task_id="task-pytorch-01",
    skill_name="pytorch",
    title="Build a Modular PyTorch Neural Network Classifier",
    difficulty="Intermediate",
    estimated_hours=3,
    role_relevance={
        "all": "Core deep learning framework used across production ML, computer vision, and transformer models.",
        "aiml_engineer": "Essential for training custom vision and tabular models, tuning loss functions, and managing GPU tensor flows.",
        "genai_engineer": "Fundamental for understanding PyTorch attention mechanisms, LoRA adapters, and transformer fine-tuning.",
        "sde": "Demonstrates capability to serve ML models, manage tensor data structures, and debug inference pipelines.",
    },
    objective="Construct a modular PyTorch neural network classifier with custom Dataset, DataLoader, multi-layer nn.Module, and a full training/validation loop with optimizer and loss evaluation.",
    description=(
        "Construct a standalone training script containing a custom torch.utils.data.Dataset, "
        "a multi-layer nn.Module class with ReLU activations, and a full training/validation loop "
        "using Adam optimizer and CrossEntropyLoss."
    ),
    deliverable="A runnable Python script `train_classifier.py` with printed evaluation loss and accuracy.",
    completion_criteria=[
        "Custom nn.Module class defined with __init__ and forward methods",
        "DataLoader configured with batching and shuffle enabled",
        "Training loop iterates over 5+ epochs and logs training vs validation loss",
        "Model parameters saved to disk using torch.save()",
    ],
    developed_skills=["python", "numpy", "matplotlib"],
)
ROADMAP_TEMPLATES["docker"] = RoadmapTaskData(
    task_id="task-docker-01",
    skill_name="docker",
    title="Containerize a Python Backend with Multi-Stage Dockerfile",
    difficulty="Intermediate",
    estimated_hours=2,
    role_relevance={
        "all": "Universal standard for packaging reproducible applications, environments, and services.",
        "aiml_engineer": "Eliminates 'works on my machine' CUDA and library version conflicts in ML deployments.",
        "genai_engineer": "Required for deploying LLM wrappers, vector store databases, and agent containers.",
        "sde": "Core devops competency for CI/CD integration, container orchestration, and cloud hosting.",
    },
    objective="Write a production multi-stage Dockerfile for a Python service using a lightweight base image, non-root security user, healthcheck, and a docker-compose.yml file.",
    description=(
        "Write a production Dockerfile for a Python service using a lightweight base image "
        "(python:3.13-slim), non-root security user, and a docker-compose.yml file."
    ),
    deliverable="`Dockerfile` and `docker-compose.yml` that successfully builds and runs locally.",
    completion_criteria=[
        "Dockerfile uses explicit base tag and clean dependency installation with no-cache",
        "Non-root user created and assigned to container process execution",
        "Healthcheck instruction defined verifying service responsiveness",
        "`docker build` and `docker run -p 8000:8000` verified working via curl",
    ],
    developed_skills=["cloud-devops", "fastapi", "git"],
)


# ---------------------------------------------------------------------------
# Public Functions
# ---------------------------------------------------------------------------

def _serialize_task(task: RoadmapTaskData, role_key: str) -> Dict:
    """Helper to serialize a RoadmapTaskData into a dictionary with learning resources."""
    relevance_text = task.role_relevance.get(
        role_key,
        task.role_relevance.get("all", "Valuable technical skill for modern engineering careers.")
    )
    resources = get_learning_resources(task.skill_name)
    return {
        "task_id": task.task_id,
        "skill_name": task.skill_name,
        "title": task.title,
        "task_title": task.title,
        "difficulty": task.difficulty,
        "estimated_hours": task.estimated_hours,
        "target_role_relevance": relevance_text,
        "role_relevance": relevance_text,
        "objective": task.objective,
        "description": task.description,
        "deliverable": task.deliverable,
        "completion_criteria": list(task.completion_criteria),
        "developed_skills": list(task.developed_skills),
        "resources": [
            {
                "title": r.title,
                "url": r.url,
                "provider": r.provider,
                "resource_type": r.resource_type,
            }
            for r in resources
        ],
    }


def get_role_roadmap(target_role: Optional[str] = "all") -> List[Dict]:
    """
    Retrieve the tailored 4-project career roadmap for the selected career role:
    - aiml_engineer: NumPy, pandas, scikit-learn, Model evaluation
    - genai_engineer: LLM API, Embeddings, RAG, LLM Application with evaluation
    - sde: Git, REST API, Database CRUD, Automated testing
    - all: Core foundation projects
    """
    role_key = (target_role or "all").lower().replace(" ", "_")
    tasks = ROLE_ROADMAPS.get(role_key, ROLE_ROADMAPS["all"])
    return [_serialize_task(task, role_key) for task in tasks]


def generate_roadmap_task(
    canonical_name: str,
    target_role: Optional[str] = "all",
) -> Optional[Dict]:
    """
    Generate an actionable roadmap task dictionary for a canonical skill gap.
    Checks role-tailored tasks first, then template library, then fallback.
    """
    role_key = (target_role or "all").lower().replace(" ", "_")
    role_tasks = ROLE_ROADMAPS.get(role_key, [])
    for t in role_tasks:
        if t.skill_name == canonical_name:
            return _serialize_task(t, role_key)

    template = ROADMAP_TEMPLATES.get(canonical_name)
    if template:
        return _serialize_task(template, role_key)

    return _build_fallback_task(canonical_name, role_key)


def _build_fallback_task(canonical_name: str, target_role: Optional[str]) -> Dict:
    """Provide a structured beginner task for skills without an explicit template."""
    resources = get_learning_resources(canonical_name)
    name_display = canonical_name.replace("-", " ").title()
    relevance_text = (
        f"Familiarity with {name_display} reinforces core engineering competency "
        "and demonstrates your capability to quickly learn and adopt tools in project work."
    )
    objective_text = (
        f"Implement a working Python module demonstrating core {name_display} functionality "
        "following official documentation quickstarts with automated unit tests."
    )

    return {
        "task_id": f"task-{canonical_name}-generic",
        "skill_name": canonical_name,
        "title": f"Implement a Working Practical Module Using {name_display}",
        "task_title": f"Implement a Working Practical Module Using {name_display}",
        "difficulty": "Beginner",
        "estimated_hours": 2,
        "target_role_relevance": relevance_text,
        "role_relevance": relevance_text,
        "objective": objective_text,
        "description": (
            f"Review the official documentation for {name_display}, then write a clean, "
            "self-contained Python module demonstrating its core functionality with automated tests."
        ),
        "deliverable": f"A Python module demonstrating core {name_display} functionality with unit tests.",
        "completion_criteria": [
            f"Install and import {canonical_name} in an isolated environment",
            "Implement a core use-case following the official documentation quickstart",
            "Add automated test cases validating standard and edge-case execution",
            "Document usage, installation steps, and code comments in a README or module docstring",
        ],
        "developed_skills": ["python", "testing"],
        "resources": [
            {
                "title": r.title,
                "url": r.url,
                "provider": r.provider,
                "resource_type": r.resource_type,
            }
            for r in resources
        ],
    }
