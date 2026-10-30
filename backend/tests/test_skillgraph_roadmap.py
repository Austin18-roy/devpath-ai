"""
test_skillgraph_roadmap.py — Unit tests for the Career Roadmap Generator.
"""

from app.services.skillgraph.roadmap import (
    generate_roadmap_task,
    get_role_roadmap,
    ROADMAP_TEMPLATES,
    ROLE_ROADMAPS,
)


def test_roadmap_task_generation_pytorch():
    task = generate_roadmap_task("pytorch", target_role="aiml_engineer")
    assert task is not None
    assert task["skill_name"] == "pytorch"
    assert "Neural Network" in task["title"]
    assert task["difficulty"] in ["Beginner", "Intermediate", "Advanced"]
    assert task["estimated_hours"] > 0
    assert "GPU" in task["target_role_relevance"] or "vision" in task["target_role_relevance"]
    assert len(task["completion_criteria"]) >= 3
    assert len(task["deliverable"]) > 10
    assert len(task["resources"]) >= 1


def test_roadmap_role_relevance_switch():
    task_aiml = generate_roadmap_task("fastapi", target_role="aiml_engineer")
    task_sde = generate_roadmap_task("fastapi", target_role="sde")
    task_genai = generate_roadmap_task("fastapi", target_role="genai_engineer")

    assert "model" in task_aiml["target_role_relevance"].lower()
    assert "backend" in task_sde["target_role_relevance"].lower() or "api" in task_sde["target_role_relevance"].lower()
    assert "streaming" in task_genai["target_role_relevance"].lower() or "endpoint" in task_genai["target_role_relevance"].lower()


def test_fallback_task_for_unlisted_skill():
    task = generate_roadmap_task("polars", target_role="all")
    assert task is not None
    assert task["skill_name"] == "polars"
    assert "Polars" in task["title"]
    assert len(task["completion_criteria"]) >= 3
    assert task["estimated_hours"] == 2
    assert len(task["objective"]) > 15
    assert len(task["role_relevance"]) > 15


def test_aiml_engineer_roadmap_tasks():
    tasks = get_role_roadmap("aiml_engineer")
    assert len(tasks) == 4
    skills = [t["skill_name"] for t in tasks]
    assert skills == ["numpy", "pandas", "scikit-learn", "model-evaluation"]
    titles = [t["title"] for t in tasks]
    assert "NumPy Numerical Computing and Regression" in titles[0]
    assert "pandas Data Cleaning and Analysis" in titles[1]
    assert "scikit-learn Machine Learning Pipeline" in titles[2]
    assert "Model Evaluation and Validation" in titles[3]
    for t in tasks:
        assert len(t["completion_criteria"]) >= 4
        assert len(t["deliverable"]) > 10
        assert len(t["resources"]) >= 1
        assert len(t["objective"]) > 20
        assert len(t["role_relevance"]) > 20


def test_genai_engineer_roadmap_tasks():
    tasks = get_role_roadmap("genai_engineer")
    assert len(tasks) == 4
    skills = [t["skill_name"] for t in tasks]
    assert skills == ["llm-api", "embeddings", "langchain", "generative-ai"]
    titles = [t["title"] for t in tasks]
    assert "LLM API Integration" in titles[0]
    assert "Embeddings and Semantic Search" in titles[1]
    assert "Retrieval-Augmented Generation (RAG)" in titles[2]
    assert "Build a Small LLM Application with Evaluation" in titles[3]
    for t in tasks:
        assert len(t["completion_criteria"]) >= 4
        assert len(t["deliverable"]) > 10
        assert len(t["resources"]) >= 1
        assert len(t["objective"]) > 20
        assert len(t["role_relevance"]) > 20


def test_sde_roadmap_tasks():
    tasks = get_role_roadmap("sde")
    assert len(tasks) == 4
    skills = [t["skill_name"] for t in tasks]
    assert skills == ["git", "fastapi", "postgresql", "pytest"]
    titles = [t["title"] for t in tasks]
    assert "Git and Collaborative Development Workflow" in titles[0]
    assert "REST API Development and Validation" in titles[1]
    assert "Database Integration and CRUD Operations" in titles[2]
    assert "Automated Testing and Software Quality" in titles[3]
    for t in tasks:
        assert len(t["completion_criteria"]) >= 4
        assert len(t["deliverable"]) > 10
        assert len(t["resources"]) >= 1
        assert len(t["objective"]) > 20
        assert len(t["role_relevance"]) > 20


def test_roles_have_distinct_intended_tasks():
    aiml_tasks = {t["title"] for t in get_role_roadmap("aiml_engineer")}
    genai_tasks = {t["title"] for t in get_role_roadmap("genai_engineer")}
    sde_tasks = {t["title"] for t in get_role_roadmap("sde")}

    # None of the 3 roles should share task titles
    assert len(aiml_tasks.intersection(genai_tasks)) == 0
    assert len(aiml_tasks.intersection(sde_tasks)) == 0
    assert len(genai_tasks.intersection(sde_tasks)) == 0


def test_every_role_task_has_non_empty_relevance_and_objective():
    """Verify that all four career options have non-empty role_relevance and objective."""
    career_roles = ["aiml_engineer", "genai_engineer", "sde", "all"]

    for role in career_roles:
        tasks = get_role_roadmap(role)
        assert len(tasks) >= 4, f"Role {role} should have at least 4 tasks"
        for task in tasks:
            # Check role relevance
            assert "role_relevance" in task, f"Missing role_relevance in {task['task_id']}"
            assert isinstance(task["role_relevance"], str)
            assert len(task["role_relevance"].strip()) >= 20, (
                f"role_relevance for {task['skill_name']} in {role} is too short or empty"
            )

            # Check target_role_relevance
            assert "target_role_relevance" in task
            assert task["target_role_relevance"] == task["role_relevance"]

            # Check objective
            assert "objective" in task, f"Missing objective in {task['task_id']}"
            assert isinstance(task["objective"], str)
            assert len(task["objective"].strip()) >= 20, (
                f"objective for {task['skill_name']} in {role} is too short or empty"
            )

            # Check title & deliverable
            assert len(task["title"].strip()) >= 5
            assert len(task["deliverable"].strip()) >= 10


def test_all_templates_have_valid_structure():
    assert len(ROADMAP_TEMPLATES) >= 10
    for name, template in ROADMAP_TEMPLATES.items():
        assert template.skill_name == name
        assert template.difficulty in ["Beginner", "Intermediate", "Advanced"]
        assert template.estimated_hours >= 1
        assert "all" in template.role_relevance
        assert len(template.completion_criteria) >= 3
        assert len(template.deliverable) > 10
        assert len(template.objective.strip()) >= 20
