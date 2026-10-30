"""
resources.py — Verified official documentation and learning resource catalogue for SkillGraph.

Principles:
- Every resource is free and accessible without a paid subscription.
- Trustworthy sources only: official project documentation, reputable open-source
  foundations (Apache, Python Software Foundation, Linux Foundation), or standard manuals.
- Zero invented URLs: all URLs are verified root portals or standard documentation paths.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class LearningResource:
    """Verified free documentation or learning material for a skill."""
    title: str
    url: str
    provider: str
    resource_type: str  # "official_docs" | "tutorial" | "handbook"


# ---------------------------------------------------------------------------
# Curated resource catalogue mapped by canonical skill name
# ---------------------------------------------------------------------------

RESOURCE_CATALOG: Dict[str, List[LearningResource]] = {
    "python": [
        LearningResource(
            title="Official Python Tutorial & Documentation",
            url="https://docs.python.org/3/",
            provider="Python Software Foundation",
            resource_type="official_docs",
        )
    ],
    "numpy": [
        LearningResource(
            title="NumPy User Guide & API Reference",
            url="https://numpy.org/doc/stable/",
            provider="NumPy Developers",
            resource_type="official_docs",
        )
    ],
    "pandas": [
        LearningResource(
            title="pandas Documentation & Getting Started Tutorials",
            url="https://pandas.pydata.org/docs/",
            provider="pandas Development Team",
            resource_type="official_docs",
        )
    ],
    "scipy": [
        LearningResource(
            title="SciPy Documentation",
            url="https://docs.scipy.org/doc/scipy/",
            provider="SciPy Community",
            resource_type="official_docs",
        )
    ],
    "matplotlib": [
        LearningResource(
            title="Matplotlib User Guide & Examples",
            url="https://matplotlib.org/stable/",
            provider="Matplotlib Development Team",
            resource_type="official_docs",
        )
    ],
    "seaborn": [
        LearningResource(
            title="Seaborn Statistical Data Visualization Guide",
            url="https://seaborn.pydata.org/",
            provider="Michael Waskom / Seaborn Team",
            resource_type="official_docs",
        )
    ],
    "scikit-learn": [
        LearningResource(
            title="scikit-learn User Guide & Machine Learning Tutorials",
            url="https://scikit-learn.org/stable/",
            provider="scikit-learn Developers",
            resource_type="official_docs",
        )
    ],
    "model-evaluation": [
        LearningResource(
            title="scikit-learn Model Evaluation & Scoring Metrics Guide",
            url="https://scikit-learn.org/stable/modules/model_evaluation.html",
            provider="scikit-learn Developers",
            resource_type="official_docs",
        )
    ],
    "xgboost": [
        LearningResource(
            title="XGBoost Documentation & Tutorials",
            url="https://xgboost.readthedocs.io/en/stable/",
            provider="DMLC",
            resource_type="official_docs",
        )
    ],
    "lightgbm": [
        LearningResource(
            title="LightGBM Documentation",
            url="https://lightgbm.readthedocs.io/en/latest/",
            provider="Microsoft Corporation",
            resource_type="official_docs",
        )
    ],
    "pytorch": [
        LearningResource(
            title="Official PyTorch Tutorials & Documentation",
            url="https://pytorch.org/docs/",
            provider="PyTorch Foundation / Linux Foundation",
            resource_type="official_docs",
        )
    ],
    "tensorflow": [
        LearningResource(
            title="TensorFlow Core Documentation & Guides",
            url="https://www.tensorflow.org/api_docs",
            provider="Google Brain / TensorFlow Team",
            resource_type="official_docs",
        )
    ],
    "keras": [
        LearningResource(
            title="Keras 3 Developer Guides & API Reference",
            url="https://keras.io/guides/",
            provider="Keras Community",
            resource_type="official_docs",
        )
    ],
    "jax": [
        LearningResource(
            title="JAX Documentation & Quickstart",
            url="https://jax.readthedocs.io/en/latest/",
            provider="Google Research",
            resource_type="official_docs",
        )
    ],
    "hugging-face": [
        LearningResource(
            title="Hugging Face Transformers Documentation",
            url="https://huggingface.co/docs",
            provider="Hugging Face",
            resource_type="official_docs",
        )
    ],
    "langchain": [
        LearningResource(
            title="LangChain Python Documentation",
            url="https://python.langchain.com/",
            provider="LangChain Inc.",
            resource_type="official_docs",
        )
    ],
    "llamaindex": [
        LearningResource(
            title="LlamaIndex Documentation & Starter Tutorials",
            url="https://docs.llamaindex.ai/en/stable/",
            provider="LlamaIndex Inc.",
            resource_type="official_docs",
        )
    ],
    "openai": [
        LearningResource(
            title="OpenAI API Documentation & Quickstarts",
            url="https://platform.openai.com/docs/overview",
            provider="OpenAI",
            resource_type="official_docs",
        )
    ],
    "llm-api": [
        LearningResource(
            title="Google Gemini API & Python SDK Guides",
            url="https://ai.google.dev/docs",
            provider="Google DeepMind",
            resource_type="official_docs",
        ),
        LearningResource(
            title="OpenAI API Documentation & Quickstarts",
            url="https://platform.openai.com/docs/overview",
            provider="OpenAI",
            resource_type="official_docs",
        ),
    ],
    "embeddings": [
        LearningResource(
            title="Sentence Transformers Documentation & Guides",
            url="https://sbert.net/",
            provider="UKP Lab / Hugging Face",
            resource_type="official_docs",
        )
    ],
    "generative-ai": [
        LearningResource(
            title="Hugging Face Open Source AI Documentation",
            url="https://huggingface.co/docs",
            provider="Hugging Face",
            resource_type="official_docs",
        )
    ],
    "chromadb": [
        LearningResource(
            title="ChromaDB Getting Started & API Reference",
            url="https://docs.trychroma.com/",
            provider="Chroma Inc.",
            resource_type="official_docs",
        )
    ],
    "faiss": [
        LearningResource(
            title="FAISS Vector Search Documentation",
            url="https://github.com/facebookresearch/faiss/wiki",
            provider="Meta AI Research",
            resource_type="official_docs",
        )
    ],
    "sentence-transformers": [
        LearningResource(
            title="Sentence Transformers Documentation",
            url="https://sbert.net/",
            provider="UKP Lab / Hugging Face",
            resource_type="official_docs",
        )
    ],
    "mlflow": [
        LearningResource(
            title="MLflow Documentation & Quickstart",
            url="https://mlflow.org/docs/latest/index.html",
            provider="Linux Foundation",
            resource_type="official_docs",
        )
    ],
    "wandb": [
        LearningResource(
            title="Weights & Biases Documentation",
            url="https://docs.wandb.ai/",
            provider="Weights & Biases",
            resource_type="official_docs",
        )
    ],
    "ray": [
        LearningResource(
            title="Ray Distributed Python Documentation",
            url="https://docs.ray.io/en/latest/",
            provider="Anyscale / Ray Community",
            resource_type="official_docs",
        )
    ],
    "dvc": [
        LearningResource(
            title="Data Version Control (DVC) Documentation",
            url="https://dvc.org/doc",
            provider="Iterative.ai",
            resource_type="official_docs",
        )
    ],
    "apache-airflow": [
        LearningResource(
            title="Apache Airflow Official Documentation",
            url="https://airflow.apache.org/docs/",
            provider="Apache Software Foundation",
            resource_type="official_docs",
        )
    ],
    "fastapi": [
        LearningResource(
            title="FastAPI Official Tutorial & Reference",
            url="https://fastapi.tiangolo.com/",
            provider="Sebastián Ramírez / FastAPI",
            resource_type="official_docs",
        )
    ],
    "flask": [
        LearningResource(
            title="Flask User Guide & Documentation",
            url="https://flask.palletsprojects.com/",
            provider="Pallets Projects",
            resource_type="official_docs",
        )
    ],
    "django": [
        LearningResource(
            title="Django Documentation & Tutorial",
            url="https://docs.djangoproject.com/",
            provider="Django Software Foundation",
            resource_type="official_docs",
        )
    ],
    "pydantic": [
        LearningResource(
            title="Pydantic Documentation",
            url="https://docs.pydantic.dev/",
            provider="Pydantic Community",
            resource_type="official_docs",
        )
    ],
    "docker": [
        LearningResource(
            title="Docker Documentation & Getting Started",
            url="https://docs.docker.com/",
            provider="Docker Inc.",
            resource_type="official_docs",
        )
    ],
    "kubernetes": [
        LearningResource(
            title="Kubernetes Basics & Official Documentation",
            url="https://kubernetes.io/docs/",
            provider="Cloud Native Computing Foundation (CNCF)",
            resource_type="official_docs",
        )
    ],
    "git": [
        LearningResource(
            title="Git Documentation & Pro Git Free Book",
            url="https://git-scm.com/docs",
            provider="Software Freedom Conservancy",
            resource_type="official_docs",
        )
    ],
    "pytest": [
        LearningResource(
            title="pytest Documentation & Best Practices",
            url="https://docs.pytest.org/",
            provider="pytest Development Team",
            resource_type="official_docs",
        )
    ],
    "postgresql": [
        LearningResource(
            title="PostgreSQL Official Documentation",
            url="https://www.postgresql.org/docs/",
            provider="PostgreSQL Global Development Group",
            resource_type="official_docs",
        )
    ],
    "sqlalchemy": [
        LearningResource(
            title="SQLAlchemy 2.0 Unified Tutorial & Documentation",
            url="https://docs.sqlalchemy.org/en/20/",
            provider="SQLAlchemy Authors",
            resource_type="official_docs",
        )
    ],
    "sqlite": [
        LearningResource(
            title="SQLite Documentation & SQL Tutorial",
            url="https://www.sqlite.org/docs.html",
            provider="SQLite Consortium",
            resource_type="official_docs",
        )
    ],
    "redis": [
        LearningResource(
            title="Redis Documentation & Commands Guide",
            url="https://redis.io/docs/",
            provider="Redis Ltd.",
            resource_type="official_docs",
        )
    ],
    "networkx": [
        LearningResource(
            title="NetworkX Tutorial & Algorithms Reference",
            url="https://networkx.org/documentation/stable/",
            provider="NetworkX Developers",
            resource_type="official_docs",
        )
    ],
    "apache-spark": [
        LearningResource(
            title="Apache Spark & PySpark Documentation",
            url="https://spark.apache.org/docs/latest/api/python/",
            provider="Apache Software Foundation",
            resource_type="official_docs",
        )
    ],
    "opencv": [
        LearningResource(
            title="OpenCV-Python Tutorials & Reference",
            url="https://docs.opencv.org/",
            provider="OpenCV Community",
            resource_type="official_docs",
        )
    ],
    "spacy": [
        LearningResource(
            title="spaCy Usage Guides & Pipelines",
            url="https://spacy.io/usage",
            provider="Explosion AI",
            resource_type="official_docs",
        )
    ],
    "google-gemini": [
        LearningResource(
            title="Google Gemini API & Python SDK Guides",
            url="https://ai.google.dev/docs",
            provider="Google DeepMind",
            resource_type="official_docs",
        )
    ],
    "aws": [
        LearningResource(
            title="AWS SDK for Python (Boto3) Documentation",
            url="https://boto3.amazonaws.com/v1/documentation/api/latest/index.html",
            provider="Amazon Web Services",
            resource_type="official_docs",
        )
    ],
}


def get_learning_resources(canonical_name: str) -> List[LearningResource]:
    """Retrieve verified free learning resources for a canonical skill."""
    return list(RESOURCE_CATALOG.get(canonical_name, []))

