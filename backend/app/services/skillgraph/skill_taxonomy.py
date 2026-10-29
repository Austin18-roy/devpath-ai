"""
skill_taxonomy.py — Canonical skill list and alias normalisation for SkillGraph.

Design principles:
- Every alias maps to exactly one canonical name.
- Aliases are lower-cased; matching is always case-insensitive.
- The taxonomy covers AIML, Generative AI, and SDE skill families
  relevant to AI/ML Engineer, SDE, and Generative AI Engineer roles.
- Entries should be real technology names (packages, tools, platforms).
  Generic programming concepts (loops, classes, etc.) are intentionally
  excluded to avoid false positives.

Extending: add entries to SKILL_ALIASES and to SKILL_METADATA.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Alias map  (alias_lower -> canonical_name)
# ---------------------------------------------------------------------------

SKILL_ALIASES: Dict[str, str] = {
    # ── AIML / Data Science ────────────────────────────────────────────────
    "numpy": "numpy",
    "np": "numpy",
    "pandas": "pandas",
    "pd": "pandas",
    "matplotlib": "matplotlib",
    "plt": "matplotlib",
    "seaborn": "seaborn",
    "sns": "seaborn",
    "scipy": "scipy",
    "sklearn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "scikit_learn": "scikit-learn",
    "xgboost": "xgboost",
    "xgb": "xgboost",
    "lightgbm": "lightgbm",
    "lgb": "lightgbm",
    "catboost": "catboost",
    "statsmodels": "statsmodels",
    "networkx": "networkx",
    "nx": "networkx",
    # ── Deep Learning ──────────────────────────────────────────────────────
    "pytorch": "pytorch",
    "torch": "pytorch",
    "tensorflow": "tensorflow",
    "tf": "tensorflow",
    "keras": "keras",
    "jax": "jax",
    "flax": "flax",
    "optax": "optax",
    "paddle": "paddlepaddle",
    "paddlepaddle": "paddlepaddle",
    "mxnet": "mxnet",
    "onnx": "onnx",
    "onnxruntime": "onnx",
    # ── Generative AI / LLM ────────────────────────────────────────────────
    "transformers": "hugging-face",
    "huggingface": "hugging-face",
    "hugging_face": "hugging-face",
    "hugging-face": "hugging-face",
    "hf": "hugging-face",
    "diffusers": "hugging-face",
    "datasets": "hugging-face",
    "peft": "hugging-face",
    "trl": "hugging-face",
    "accelerate": "hugging-face",
    "openai": "openai",
    "anthropic": "anthropic",
    "langchain": "langchain",
    "langchain_core": "langchain",
    "langchain_community": "langchain",
    "langgraph": "langchain",
    "llamaindex": "llamaindex",
    "llama_index": "llamaindex",
    "llama-index": "llamaindex",
    "llama_cpp": "llama.cpp",
    "llama.cpp": "llama.cpp",
    "ollama": "ollama",
    "groq": "groq",
    "cohere": "cohere",
    "mistral": "mistral",
    "gemini": "google-gemini",
    "google.generativeai": "google-gemini",
    "vertexai": "google-vertex-ai",
    "vertex_ai": "google-vertex-ai",
    "google.cloud.aiplatform": "google-vertex-ai",
    "autogen": "autogen",
    "crewai": "crewai",
    "crew_ai": "crewai",
    "haystack": "haystack",
    "semantic_kernel": "semantic-kernel",
    "semantic-kernel": "semantic-kernel",
    # ── Vector / Retrieval ─────────────────────────────────────────────────
    "faiss": "faiss",
    "chromadb": "chromadb",
    "chroma": "chromadb",
    "pinecone": "pinecone",
    "weaviate": "weaviate",
    "qdrant": "qdrant",
    "milvus": "milvus",
    "annoy": "annoy",
    "sentence_transformers": "sentence-transformers",
    "sentence-transformers": "sentence-transformers",
    # ── MLOps / Experiment Tracking ────────────────────────────────────────
    "mlflow": "mlflow",
    "wandb": "wandb",
    "neptune": "neptune",
    "comet_ml": "comet-ml",
    "optuna": "optuna",
    "ray": "ray",
    "ray.tune": "ray",
    "ray.serve": "ray",
    "bentoml": "bentoml",
    "triton": "triton-inference-server",
    "tritonclient": "triton-inference-server",
    "torchserve": "torchserve",
    "dvc": "dvc",
    "airflow": "apache-airflow",
    "apache_airflow": "apache-airflow",
    "prefect": "prefect",
    "dagster": "dagster",
    "great_expectations": "great-expectations",
    # ── Data Engineering ───────────────────────────────────────────────────
    "pyspark": "apache-spark",
    "spark": "apache-spark",
    "dask": "dask",
    "polars": "polars",
    "pyarrow": "apache-arrow",
    "arrow": "apache-arrow",
    "kafka": "apache-kafka",
    "confluent_kafka": "apache-kafka",
    "flink": "apache-flink",
    "dbt": "dbt",
    "sqlalchemy": "sqlalchemy",
    "alembic": "alembic",
    # ── Backend / API ──────────────────────────────────────────────────────
    "fastapi": "fastapi",
    "flask": "flask",
    "django": "django",
    "starlette": "starlette",
    "uvicorn": "uvicorn",
    "gunicorn": "gunicorn",
    "aiohttp": "aiohttp",
    "httpx": "httpx",
    "requests": "requests",
    "pydantic": "pydantic",
    "celery": "celery",
    "redis": "redis",
    "rq": "rq",
    "grpc": "grpc",
    "grpcio": "grpc",
    "graphql": "graphql",
    "strawberry": "graphql",
    "ariadne": "graphql",
    # ── Cloud / Infrastructure ─────────────────────────────────────────────
    "boto3": "aws",
    "botocore": "aws",
    "sagemaker": "aws-sagemaker",
    "google.cloud": "google-cloud",
    "gcloud": "google-cloud",
    "azure": "azure",
    "docker": "docker",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "helm": "helm",
    "terraform": "terraform",
    "ansible": "ansible",
    "github_actions": "github-actions",
    # ── Databases ──────────────────────────────────────────────────────────
    "psycopg2": "postgresql",
    "psycopg": "postgresql",
    "asyncpg": "postgresql",
    "pymysql": "mysql",
    "mysql": "mysql",
    "sqlite3": "sqlite",
    "pymongo": "mongodb",
    "mongodb": "mongodb",
    "motor": "mongodb",
    "elasticsearch": "elasticsearch",
    "opensearch": "opensearch",
    # ── Testing ────────────────────────────────────────────────────────────
    "pytest": "pytest",
    "unittest": "python-unittest",
    "hypothesis": "hypothesis",
    # ── General Python tooling ─────────────────────────────────────────────
    "git": "git",
    "pydantic": "pydantic",
    "typing": "python",
    "asyncio": "python-asyncio",
    "multiprocessing": "python",
    "concurrent": "python",
    "pathlib": "python",
    # ── Computer Vision ────────────────────────────────────────────────────
    "cv2": "opencv",
    "opencv": "opencv",
    "pillow": "pillow",
    "pil": "pillow",
    "imageio": "imageio",
    "skimage": "scikit-image",
    "scikit_image": "scikit-image",
    # ── NLP (non-HF) ───────────────────────────────────────────────────────
    "spacy": "spacy",
    "nltk": "nltk",
    "gensim": "gensim",
    "textblob": "textblob",
}


# ---------------------------------------------------------------------------
# Skill metadata — description and gap recommendations
# ---------------------------------------------------------------------------

@dataclass
class SkillInfo:
    """Metadata about a canonical skill."""
    canonical_name: str
    family: str           # "aiml" | "genai" | "sde" | "data-engineering" | "mlops"
    description: str
    recommendation: str   # Actionable advice when no/weak evidence is found
    # Keyword hints: additional non-package terms to search in JD text
    jd_keywords: List[str] = field(default_factory=list)


SKILL_METADATA: Dict[str, SkillInfo] = {
    "numpy": SkillInfo(
        canonical_name="numpy",
        family="aiml",
        description="Numerical computing with N-dimensional arrays.",
        recommendation="Add a script that uses NumPy arrays for data manipulation or matrix operations.",
        jd_keywords=["numerical computing", "array operations"],
    ),
    "pandas": SkillInfo(
        canonical_name="pandas",
        family="aiml",
        description="DataFrame-based data analysis and manipulation.",
        recommendation="Add a data cleaning or EDA script using pandas DataFrames.",
        jd_keywords=["data analysis", "dataframe", "data manipulation"],
    ),
    "matplotlib": SkillInfo(
        canonical_name="matplotlib",
        family="aiml",
        description="2D plotting and data visualization library.",
        recommendation="Add a visualisation script with matplotlib charts.",
        jd_keywords=["data visualization", "plotting"],
    ),
    "seaborn": SkillInfo(
        canonical_name="seaborn",
        family="aiml",
        description="Statistical data visualisation built on matplotlib.",
        recommendation="Add seaborn plots to your EDA notebook or script.",
        jd_keywords=["data visualization", "statistical plots"],
    ),
    "scipy": SkillInfo(
        canonical_name="scipy",
        family="aiml",
        description="Scientific computing: statistics, optimization, signal processing.",
        recommendation="Add a statistical analysis or optimisation script using scipy.",
        jd_keywords=["scientific computing", "optimization", "statistics"],
    ),
    "scikit-learn": SkillInfo(
        canonical_name="scikit-learn",
        family="aiml",
        description="Classical ML: classification, regression, clustering, pipelines.",
        recommendation=(
            "Add a supervised-learning pipeline: data split, model training "
            "(e.g. RandomForest), cross-validation, and evaluation metrics."
        ),
        jd_keywords=["machine learning", "ml", "classification", "regression", "clustering"],
    ),
    "xgboost": SkillInfo(
        canonical_name="xgboost",
        family="aiml",
        description="Gradient boosting framework widely used in tabular ML.",
        recommendation="Add an XGBoost model training script with feature importance analysis.",
        jd_keywords=["gradient boosting", "boosting", "tabular ml"],
    ),
    "lightgbm": SkillInfo(
        canonical_name="lightgbm",
        family="aiml",
        description="Fast gradient boosting for tabular data.",
        recommendation="Add a LightGBM training script comparing it to a baseline model.",
        jd_keywords=["gradient boosting", "tabular ml"],
    ),
    "pytorch": SkillInfo(
        canonical_name="pytorch",
        family="aiml",
        description="Dynamic deep learning framework for research and production.",
        recommendation=(
            "Add a PyTorch training loop: custom Dataset, DataLoader, nn.Module subclass, "
            "loss function, optimiser, and evaluation."
        ),
        jd_keywords=["deep learning", "neural network", "pytorch", "dl"],
    ),
    "tensorflow": SkillInfo(
        canonical_name="tensorflow",
        family="aiml",
        description="End-to-end ML platform from Google.",
        recommendation=(
            "Add a TensorFlow/Keras model: define layers, compile with optimizer and loss, "
            "fit on data, and evaluate."
        ),
        jd_keywords=["deep learning", "neural network", "tensorflow", "dl"],
    ),
    "keras": SkillInfo(
        canonical_name="keras",
        family="aiml",
        description="High-level neural network API (runs on TensorFlow/JAX/PyTorch).",
        recommendation="Add a Keras Sequential or Functional API model with training history plotting.",
        jd_keywords=["deep learning", "neural network"],
    ),
    "jax": SkillInfo(
        canonical_name="jax",
        family="aiml",
        description="High-performance numerical computing with autograd and XLA.",
        recommendation="Add a JAX function using jit, grad, and vmap for accelerated computation.",
        jd_keywords=["jax", "autograd", "xla"],
    ),
    "hugging-face": SkillInfo(
        canonical_name="hugging-face",
        family="genai",
        description="Transformer models, tokenisers, datasets, and fine-tuning tools.",
        recommendation=(
            "Add a script that loads a pre-trained model from the Hub "
            "(e.g. text classification or summarisation pipeline) using transformers."
        ),
        jd_keywords=["transformers", "llm", "fine-tuning", "hugging face", "hf"],
    ),
    "openai": SkillInfo(
        canonical_name="openai",
        family="genai",
        description="OpenAI API client for GPT models, embeddings, and image generation.",
        recommendation=(
            "Add a script calling the OpenAI API (or an OpenAI-compatible local endpoint) "
            "for a chat completion or embedding use case."
        ),
        jd_keywords=["gpt", "openai api", "chatgpt", "llm"],
    ),
    "langchain": SkillInfo(
        canonical_name="langchain",
        family="genai",
        description="Framework for building LLM-powered chains, agents, and RAG pipelines.",
        recommendation=(
            "Add a LangChain chain or agent: prompt template, LLM call, "
            "and at least one tool or retriever."
        ),
        jd_keywords=["langchain", "rag", "agent", "llm pipeline", "chain"],
    ),
    "llamaindex": SkillInfo(
        canonical_name="llamaindex",
        family="genai",
        description="Data framework for LLM-powered indexing and retrieval.",
        recommendation="Add a LlamaIndex script that indexes documents and answers queries.",
        jd_keywords=["llamaindex", "rag", "document indexing"],
    ),
    "faiss": SkillInfo(
        canonical_name="faiss",
        family="genai",
        description="Facebook AI Similarity Search — fast vector similarity lookups.",
        recommendation="Add a FAISS index that stores embeddings and performs nearest-neighbour search.",
        jd_keywords=["vector search", "similarity search", "embeddings"],
    ),
    "chromadb": SkillInfo(
        canonical_name="chromadb",
        family="genai",
        description="Open-source embedding database for LLM applications.",
        recommendation="Add a ChromaDB collection: embed documents, upsert, and query.",
        jd_keywords=["vector database", "vector store", "embeddings"],
    ),
    "sentence-transformers": SkillInfo(
        canonical_name="sentence-transformers",
        family="genai",
        description="Sentence and document embeddings using transformer models.",
        recommendation="Add a script that generates sentence embeddings and computes cosine similarity.",
        jd_keywords=["embeddings", "sentence embeddings", "semantic similarity"],
    ),
    "mlflow": SkillInfo(
        canonical_name="mlflow",
        family="mlops",
        description="ML experiment tracking, model registry, and deployment.",
        recommendation=(
            "Add MLflow logging to an existing training script: "
            "log parameters, metrics, and register the model."
        ),
        jd_keywords=["experiment tracking", "model registry", "mlops"],
    ),
    "wandb": SkillInfo(
        canonical_name="wandb",
        family="mlops",
        description="Weights & Biases — experiment tracking and model visualisation.",
        recommendation="Add wandb.init(), wandb.log(), and a run summary to a training script.",
        jd_keywords=["experiment tracking", "model monitoring"],
    ),
    "ray": SkillInfo(
        canonical_name="ray",
        family="mlops",
        description="Distributed Python framework for ML training, tuning, and serving.",
        recommendation="Add a Ray remote function or Ray Tune hyperparameter search.",
        jd_keywords=["distributed training", "hyperparameter tuning"],
    ),
    "dvc": SkillInfo(
        canonical_name="dvc",
        family="mlops",
        description="Data version control for ML datasets and pipeline reproducibility.",
        recommendation="Add a dvc.yaml pipeline file tracking a data preprocessing and training stage.",
        jd_keywords=["data versioning", "pipeline", "mlops"],
    ),
    "apache-airflow": SkillInfo(
        canonical_name="apache-airflow",
        family="mlops",
        description="Workflow orchestration for data pipelines and ML jobs.",
        recommendation="Add a simple Airflow DAG with Python operators for a data processing pipeline.",
        jd_keywords=["workflow orchestration", "dag", "pipeline", "airflow"],
    ),
    "fastapi": SkillInfo(
        canonical_name="fastapi",
        family="sde",
        description="Modern Python web API framework with automatic OpenAPI docs.",
        recommendation=(
            "Add a FastAPI endpoint with a Pydantic request model, "
            "error handling, and a pytest integration test."
        ),
        jd_keywords=["rest api", "web api", "backend", "api development"],
    ),
    "flask": SkillInfo(
        canonical_name="flask",
        family="sde",
        description="Lightweight Python web micro-framework.",
        recommendation="Add a Flask blueprint with at least one route, request validation, and a test.",
        jd_keywords=["web framework", "rest api", "backend"],
    ),
    "django": SkillInfo(
        canonical_name="django",
        family="sde",
        description="Full-featured Python web framework with ORM and admin.",
        recommendation="Add a Django app with a model, view, URL route, and a simple test.",
        jd_keywords=["web framework", "orm", "django", "backend"],
    ),
    "docker": SkillInfo(
        canonical_name="docker",
        family="sde",
        description="Container runtime for packaging and deploying applications.",
        recommendation=(
            "Add a Dockerfile and docker-compose.yml to containerise the backend, "
            "and verify it builds and runs."
        ),
        jd_keywords=["docker", "containers", "containerization", "containerisation"],
    ),
    "kubernetes": SkillInfo(
        canonical_name="kubernetes",
        family="sde",
        description="Container orchestration platform.",
        recommendation=(
            "Add Kubernetes manifests (Deployment, Service) to deploy the backend, "
            "or a Helm chart with configurable replicas."
        ),
        jd_keywords=["kubernetes", "k8s", "container orchestration"],
    ),
    "aws": SkillInfo(
        canonical_name="aws",
        family="sde",
        description="Amazon Web Services cloud platform.",
        recommendation=(
            "Add a boto3 script that uses at least one AWS service "
            "(e.g. S3 upload/download, SQS message, Lambda invocation)."
        ),
        jd_keywords=["aws", "amazon web services", "cloud", "s3", "ec2", "lambda"],
    ),
    "google-cloud": SkillInfo(
        canonical_name="google-cloud",
        family="sde",
        description="Google Cloud Platform services.",
        recommendation=(
            "Add a google-cloud-storage or BigQuery script demonstrating "
            "a basic GCP service interaction."
        ),
        jd_keywords=["gcp", "google cloud", "google cloud platform"],
    ),
    "apache-spark": SkillInfo(
        canonical_name="apache-spark",
        family="data-engineering",
        description="Distributed data processing engine.",
        recommendation="Add a PySpark job that reads a dataset, transforms it, and writes the output.",
        jd_keywords=["spark", "big data", "distributed computing", "pyspark"],
    ),
    "postgresql": SkillInfo(
        canonical_name="postgresql",
        family="sde",
        description="Relational database system.",
        recommendation=(
            "Add a script using psycopg2 or SQLAlchemy to create a table, "
            "insert rows, and run a parameterised query."
        ),
        jd_keywords=["postgresql", "postgres", "relational database", "sql", "rdbms"],
    ),
    "sql": SkillInfo(
        canonical_name="sql",
        family="sde",
        description="Structured Query Language for relational databases.",
        recommendation=(
            "Add SQLAlchemy ORM models or raw SQL queries with parameterised inputs, "
            "and a test that verifies query output."
        ),
        jd_keywords=["sql", "database queries", "relational database"],
    ),
    "sqlite": SkillInfo(
        canonical_name="sqlite",
        family="sde",
        description="Embedded relational database.",
        recommendation="Add a sqlite3 script that creates a schema, inserts data, and queries it.",
        jd_keywords=["sqlite", "embedded database"],
    ),
    "redis": SkillInfo(
        canonical_name="redis",
        family="sde",
        description="In-memory key-value store for caching and messaging.",
        recommendation="Add a redis-py script demonstrating cache set/get and TTL expiry.",
        jd_keywords=["redis", "caching", "in-memory cache"],
    ),
    "git": SkillInfo(
        canonical_name="git",
        family="sde",
        description="Distributed version control system.",
        recommendation=(
            "Ensure your repository has a clear commit history, "
            "meaningful commit messages, and a branch strategy documented in README."
        ),
        jd_keywords=["git", "version control", "github", "gitlab"],
    ),
    "pytest": SkillInfo(
        canonical_name="pytest",
        family="sde",
        description="Python testing framework.",
        recommendation="Add pytest tests for all critical functions, including edge cases.",
        jd_keywords=["testing", "unit testing", "pytest", "test-driven development"],
    ),
    "pydantic": SkillInfo(
        canonical_name="pydantic",
        family="sde",
        description="Data validation and settings management using Python type hints.",
        recommendation="Define Pydantic models for all API request/response schemas in your project.",
        jd_keywords=["data validation", "pydantic", "type safety"],
    ),
    "networkx": SkillInfo(
        canonical_name="networkx",
        family="aiml",
        description="Graph analysis and algorithms library.",
        recommendation=(
            "Add a NetworkX script that constructs a directed graph, "
            "runs a shortest-path or centrality algorithm, and visualises the result."
        ),
        jd_keywords=["graph analysis", "network analysis", "graph algorithms"],
    ),
    "spacy": SkillInfo(
        canonical_name="spacy",
        family="aiml",
        description="Industrial-strength NLP library.",
        recommendation="Add a spaCy pipeline: named entity recognition or dependency parsing on sample text.",
        jd_keywords=["nlp", "natural language processing", "ner", "text processing"],
    ),
    "nltk": SkillInfo(
        canonical_name="nltk",
        family="aiml",
        description="Natural Language Toolkit for text processing.",
        recommendation="Add NLTK tokenisation, stemming, and stopword removal to a text-processing script.",
        jd_keywords=["nlp", "natural language processing", "text processing"],
    ),
    "opencv": SkillInfo(
        canonical_name="opencv",
        family="aiml",
        description="Computer vision library.",
        recommendation="Add an OpenCV script: load an image, apply a transform, and display/save results.",
        jd_keywords=["computer vision", "image processing", "cv"],
    ),
    "pillow": SkillInfo(
        canonical_name="pillow",
        family="aiml",
        description="Python imaging library for image manipulation.",
        recommendation="Add Pillow image loading, resizing, and format conversion to a utility script.",
        jd_keywords=["image processing", "image manipulation"],
    ),
    "sqlalchemy": SkillInfo(
        canonical_name="sqlalchemy",
        family="sde",
        description="Python SQL toolkit and ORM.",
        recommendation="Add SQLAlchemy ORM models, a session factory, and CRUD helper functions.",
        jd_keywords=["orm", "database", "sqlalchemy"],
    ),
    "celery": SkillInfo(
        canonical_name="celery",
        family="sde",
        description="Distributed task queue for async and scheduled jobs.",
        recommendation="Add a Celery task with a Redis or RabbitMQ broker in the project configuration.",
        jd_keywords=["task queue", "async tasks", "background jobs"],
    ),
    "dask": SkillInfo(
        canonical_name="dask",
        family="data-engineering",
        description="Parallel computing library scaling pandas and NumPy.",
        recommendation="Add a Dask DataFrame pipeline for a large-scale data transformation.",
        jd_keywords=["parallel computing", "big data", "dask"],
    ),
    "polars": SkillInfo(
        canonical_name="polars",
        family="data-engineering",
        description="Fast DataFrame library written in Rust.",
        recommendation="Add a Polars EDA script and benchmark it against pandas on the same dataset.",
        jd_keywords=["dataframe", "data processing"],
    ),
    "google-gemini": SkillInfo(
        canonical_name="google-gemini",
        family="genai",
        description="Google Gemini multimodal LLM API.",
        recommendation="Add a script calling google-generativeai to generate text or analyse an image.",
        jd_keywords=["gemini", "google ai", "multimodal llm"],
    ),
    "google-vertex-ai": SkillInfo(
        canonical_name="google-vertex-ai",
        family="genai",
        description="Google Cloud Vertex AI managed ML platform.",
        recommendation="Add a Vertex AI training job or online prediction endpoint call.",
        jd_keywords=["vertex ai", "google cloud ml", "managed ml"],
    ),
    "aws-sagemaker": SkillInfo(
        canonical_name="aws-sagemaker",
        family="mlops",
        description="AWS managed ML training and deployment service.",
        recommendation="Add a SageMaker training job or endpoint deployment script using the sagemaker SDK.",
        jd_keywords=["sagemaker", "aws ml", "managed ml training"],
    ),
    "onnx": SkillInfo(
        canonical_name="onnx",
        family="mlops",
        description="Open Neural Network Exchange format for model interoperability.",
        recommendation="Export a trained model to ONNX and verify inference with onnxruntime.",
        jd_keywords=["model export", "onnx", "model deployment"],
    ),
    "grpc": SkillInfo(
        canonical_name="grpc",
        family="sde",
        description="High-performance RPC framework.",
        recommendation="Add a gRPC service definition (.proto) and a Python server + client implementation.",
        jd_keywords=["grpc", "rpc", "microservices"],
    ),
    "mongodb": SkillInfo(
        canonical_name="mongodb",
        family="sde",
        description="Document-oriented NoSQL database.",
        recommendation="Add a pymongo or Motor script with CRUD operations and an index.",
        jd_keywords=["mongodb", "nosql", "document database"],
    ),
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def normalise_alias(raw: str) -> Optional[str]:
    """
    Return the canonical skill name for a raw alias string, or None if unknown.
    Matching is case-insensitive and strips surrounding whitespace.
    """
    key = raw.strip().lower()
    return SKILL_ALIASES.get(key)


def get_skill_info(canonical_name: str) -> Optional[SkillInfo]:
    """Return SkillInfo for a canonical name, or None if not in taxonomy."""
    return SKILL_METADATA.get(canonical_name)


def all_canonical_names() -> List[str]:
    """Return the deduplicated sorted list of all canonical skill names."""
    return sorted(set(SKILL_ALIASES.values()))


def aliases_for(canonical_name: str) -> List[str]:
    """Return all aliases that map to the given canonical name."""
    return [alias for alias, canon in SKILL_ALIASES.items() if canon == canonical_name]

