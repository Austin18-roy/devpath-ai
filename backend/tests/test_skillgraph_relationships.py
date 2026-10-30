"""
test_skillgraph_relationships.py — Unit tests for SkillRelationshipNetwork & learning resources.
"""

from app.services.skillgraph.relationships import SkillRelationshipNetwork, skill_relationship_network
from app.services.skillgraph.resources import get_learning_resources, RESOURCE_CATALOG


def test_network_instantiation():
    net = SkillRelationshipNetwork()
    assert len(net.graph.nodes) > 30
    assert len(net.graph.edges) > 30


def test_pytorch_relationships():
    related = skill_relationship_network.get_related_skills("pytorch")
    assert len(related) > 0
    # Should contain complements or prerequisites like numpy or domain peers
    assert any(s in related for s in ["numpy", "hugging-face", "tensorflow", "keras"])


def test_fastapi_complements():
    complements = skill_relationship_network.get_complements("fastapi")
    assert "pydantic" in complements or "docker" in complements or "pytest" in complements


def test_skill_domain():
    assert skill_relationship_network.get_skill_domain("pytorch") == "deep-learning"
    assert skill_relationship_network.get_skill_domain("fastapi") == "backend-api"
    assert skill_relationship_network.get_skill_domain("docker") == "cloud-devops"
    assert skill_relationship_network.get_skill_domain("nonexistent_xyz") is None


def test_learning_resources_validity():
    assert len(RESOURCE_CATALOG) > 20
    for skill, resources in RESOURCE_CATALOG.items():
        assert len(resources) > 0
        for res in resources:
            assert res.url.startswith("https://")
            assert len(res.title) > 5
            assert len(res.provider) > 2


def test_get_learning_resources_known_and_unknown():
    python_docs = get_learning_resources("python")
    assert len(python_docs) >= 1
    assert "docs.python.org" in python_docs[0].url

    unknown = get_learning_resources("unknown_fantasy_tool_999")
    assert unknown == []

