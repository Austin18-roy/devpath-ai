"""
relationships.py — Deterministic skill relationship and ontology network.

Built with NetworkX to model:
- Subconcepts & domains (e.g., PyTorch -> Deep Learning)
- Complementary technologies (e.g., FastAPI <-> Pydantic, Docker <-> Kubernetes)
- Prerequisites (e.g., Python -> NumPy -> PyTorch)

Zero external AI dependencies, zero network calls, 100% deterministic and instant.
"""

from typing import Dict, List, Optional, Set
import networkx as nx


class SkillRelationshipNetwork:
    """NetworkX-backed directed knowledge graph of tech skills and engineering domains."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_network()

    def _build_network(self) -> None:
        """Construct the ontology graph with domains, skills, and typed relationships."""
        # Domain clusters
        domains = [
            "deep-learning",
            "machine-learning",
            "generative-ai",
            "data-engineering",
            "mlops",
            "backend-api",
            "cloud-devops",
            "databases",
        ]
        for d in domains:
            self.graph.add_node(d, node_type="domain", label=d.replace("-", " ").title())

        # Skill -> Domain mappings (subconcept_of)
        skill_domains = {
            "pytorch": "deep-learning",
            "tensorflow": "deep-learning",
            "keras": "deep-learning",
            "jax": "deep-learning",
            "opencv": "deep-learning",
            "scikit-learn": "machine-learning",
            "xgboost": "machine-learning",
            "lightgbm": "machine-learning",
            "networkx": "machine-learning",
            "spacy": "machine-learning",
            "nltk": "machine-learning",
            "hugging-face": "generative-ai",
            "langchain": "generative-ai",
            "llamaindex": "generative-ai",
            "openai": "generative-ai",
            "google-gemini": "generative-ai",
            "chromadb": "generative-ai",
            "faiss": "generative-ai",
            "sentence-transformers": "generative-ai",
            "numpy": "data-engineering",
            "pandas": "data-engineering",
            "polars": "data-engineering",
            "apache-spark": "data-engineering",
            "dask": "data-engineering",
            "scipy": "data-engineering",
            "fastapi": "backend-api",
            "flask": "backend-api",
            "django": "backend-api",
            "pydantic": "backend-api",
            "pytest": "backend-api",
            "docker": "cloud-devops",
            "kubernetes": "cloud-devops",
            "aws": "cloud-devops",
            "google-cloud": "cloud-devops",
            "git": "cloud-devops",
            "mlflow": "mlops",
            "wandb": "mlops",
            "dvc": "mlops",
            "apache-airflow": "mlops",
            "ray": "mlops",
            "postgresql": "databases",
            "sqlite": "databases",
            "redis": "databases",
            "mongodb": "databases",
            "sql": "databases",
            "sqlalchemy": "databases",
            "matplotlib": "data-engineering",
            "seaborn": "data-engineering",
            "python": "backend-api",
        }

        for skill, domain in skill_domains.items():
            self.graph.add_node(skill, node_type="skill", domain=domain)
            self.graph.add_edge(skill, domain, relation="subconcept_of")

        # Complementary pairs (bidirectional)
        complements = [
            ("fastapi", "pydantic"),
            ("fastapi", "pytest"),
            ("fastapi", "docker"),
            ("docker", "kubernetes"),
            ("pytorch", "numpy"),
            ("pytorch", "hugging-face"),
            ("pytorch", "torchvision"),
            ("tensorflow", "keras"),
            ("langchain", "chromadb"),
            ("langchain", "openai"),
            ("langchain", "hugging-face"),
            ("llamaindex", "chromadb"),
            ("pandas", "numpy"),
            ("pandas", "matplotlib"),
            ("matplotlib", "seaborn"),
            ("scikit-learn", "pandas"),
            ("scikit-learn", "numpy"),
            ("scikit-learn", "scipy"),
            ("mlflow", "pytorch"),
            ("mlflow", "scikit-learn"),
            ("postgresql", "sqlalchemy"),
            ("redis", "celery"),
            ("dvc", "git"),
            ("git", "github-actions"),
        ]

        for s1, s2 in complements:
            self.graph.add_edge(s1, s2, relation="complements")
            self.graph.add_edge(s2, s1, relation="complements")

        # Prerequisites (s1 must be learned/used before s2)
        prerequisites = [
            ("python", "numpy"),
            ("python", "fastapi"),
            ("python", "pytest"),
            ("numpy", "pandas"),
            ("numpy", "scikit-learn"),
            ("numpy", "pytorch"),
            ("pytorch", "hugging-face"),
            ("docker", "kubernetes"),
            ("sql", "postgresql"),
            ("fastapi", "docker"),
        ]

        for prereq, target in prerequisites:
            self.graph.add_edge(prereq, target, relation="prerequisite_for")

    def get_related_skills(self, canonical_name: str, limit: int = 5) -> List[str]:
        """
        Return a deduplicated list of skills closely related to canonical_name:
        Includes complementary skills, prerequisites, and peer skills sharing the same domain.
        """
        if canonical_name not in self.graph:
            return []

        related: Set[str] = set()

        # 1. Direct complements
        for neighbor in self.graph.neighbors(canonical_name):
            edge_data = self.graph.get_edge_data(canonical_name, neighbor)
            if edge_data and edge_data.get("relation") == "complements":
                if neighbor != canonical_name and self.graph.nodes[neighbor].get("node_type") == "skill":
                    related.add(neighbor)

        # 2. Inbound complements
        for pred in self.graph.predecessors(canonical_name):
            edge_data = self.graph.get_edge_data(pred, canonical_name)
            if edge_data and edge_data.get("relation") == "complements":
                if pred != canonical_name and self.graph.nodes[pred].get("node_type") == "skill":
                    related.add(pred)

        # 3. Prerequisites
        for pred in self.graph.predecessors(canonical_name):
            edge_data = self.graph.get_edge_data(pred, canonical_name)
            if edge_data and edge_data.get("relation") == "prerequisite_for":
                if pred != canonical_name and self.graph.nodes[pred].get("node_type") == "skill":
                    related.add(pred)

        # 4. Domain peers
        domain = self.get_skill_domain(canonical_name)
        if domain and domain in self.graph:
            for peer in self.graph.predecessors(domain):
                if peer != canonical_name and self.graph.nodes[peer].get("node_type") == "skill":
                    related.add(peer)

        # Return sorted by relevance, excluding self
        result = [s for s in sorted(related) if s != canonical_name]
        return result[:limit]

    def get_skill_domain(self, canonical_name: str) -> Optional[str]:
        """Return the primary engineering domain name for this skill."""
        if canonical_name not in self.graph:
            return None
        return self.graph.nodes[canonical_name].get("domain")

    def get_complements(self, canonical_name: str) -> List[str]:
        """Return skills that directly complement this skill."""
        if canonical_name not in self.graph:
            return []
        comps = []
        for n in self.graph.neighbors(canonical_name):
            if self.graph.get_edge_data(canonical_name, n).get("relation") == "complements":
                if self.graph.nodes[n].get("node_type") == "skill":
                    comps.append(n)
        return sorted(set(comps))


# Global singleton instance
skill_relationship_network = SkillRelationshipNetwork()

