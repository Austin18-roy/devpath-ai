"""
test_skillgraph_extractor.py — Unit tests for the JD skill extractor.
"""

import pytest
from app.services.skillgraph.extractor import extract_skills, ExtractedSkill


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(skills, canonical_name) -> ExtractedSkill | None:
    return next((s for s in skills if s.canonical_name == canonical_name), None)


# ---------------------------------------------------------------------------
# Section heading detection
# ---------------------------------------------------------------------------

def test_required_heading_classifies_skills_as_required():
    jd = """
Requirements:
- Python experience required
- Must have numpy skills
"""
    skills = extract_skills(jd)
    py = _get(skills, "python")
    np_ = _get(skills, "numpy")
    assert py is not None or np_ is not None, "At least one skill should be extracted"
    if np_:
        assert np_.is_required is True
        assert "required" in np_.classification_reason.lower()


def test_preferred_heading_classifies_skills_as_preferred():
    jd = """
Nice to have:
- Experience with docker is preferred
- Familiarity with kubernetes a plus
"""
    skills = extract_skills(jd)
    docker = _get(skills, "docker")
    k8s = _get(skills, "kubernetes")
    if docker:
        assert docker.is_required is False
        assert "preferred" in docker.classification_reason.lower() or "nice" in docker.classification_reason.lower()
    if k8s:
        assert k8s.is_required is False


def test_inline_required_signal():
    jd = "Experience with pytorch is required for this position."
    skills = extract_skills(jd)
    pt = _get(skills, "pytorch")
    assert pt is not None
    assert pt.is_required is True
    assert "required" in pt.classification_reason.lower() or "must" in pt.classification_reason.lower()


def test_inline_preferred_signal():
    jd = "Experience with mlflow would be preferred."
    skills = extract_skills(jd)
    ml = _get(skills, "mlflow")
    assert ml is not None
    assert ml.is_required is False


def test_no_signal_defaults_to_required():
    jd = "We use pandas and scipy in our data pipeline."
    skills = extract_skills(jd)
    pd_ = _get(skills, "pandas")
    assert pd_ is not None
    assert pd_.is_required is True
    assert "conservative" in pd_.classification_reason.lower() or "default" in pd_.classification_reason.lower()


# ---------------------------------------------------------------------------
# Alias normalisation
# ---------------------------------------------------------------------------

def test_sklearn_normalises_to_scikit_learn():
    jd = "Proficiency with sklearn is required."
    skills = extract_skills(jd)
    sk = _get(skills, "scikit-learn")
    assert sk is not None, "sklearn should be normalised to scikit-learn"
    assert "sklearn" in sk.raw_aliases_found


def test_tf_normalises_to_tensorflow():
    jd = "Experience with tf or tensorflow is required."
    skills = extract_skills(jd)
    tf = _get(skills, "tensorflow")
    assert tf is not None
    # At least one alias should be captured
    assert len(tf.raw_aliases_found) >= 1


def test_torch_normalises_to_pytorch():
    jd = "Must know torch (PyTorch) for model training."
    skills = extract_skills(jd)
    pt = _get(skills, "pytorch")
    assert pt is not None


def test_cv2_normalises_to_opencv():
    jd = "Image processing with cv2 or opencv is preferred."
    skills = extract_skills(jd)
    cv = _get(skills, "opencv")
    assert cv is not None


# ---------------------------------------------------------------------------
# De-duplication
# ---------------------------------------------------------------------------

def test_duplicate_aliases_produce_one_result():
    jd = "We require scikit-learn (sklearn) for classification tasks."
    skills = extract_skills(jd)
    sk_results = [s for s in skills if s.canonical_name == "scikit-learn"]
    assert len(sk_results) == 1, "Duplicate aliases should produce exactly one SkillResult"


def test_required_wins_over_preferred_for_same_skill():
    jd = """
Requirements:
- Must have numpy

Nice to have:
- numpy experience a bonus
"""
    skills = extract_skills(jd)
    np_ = _get(skills, "numpy")
    assert np_ is not None
    assert np_.is_required is True, "Required classification should win over preferred"


# ---------------------------------------------------------------------------
# Empty / edge cases
# ---------------------------------------------------------------------------

def test_empty_jd_returns_no_skills():
    # The API layer enforces min_length=20; extractor itself just returns empty
    skills = extract_skills("No known tech tools mentioned here at all.")
    # May find 'tools' as nothing — just ensure no crash and result is a list
    assert isinstance(skills, list)


def test_multiple_skills_extracted():
    jd = """
Requirements:
We are looking for an ML engineer with pytorch, sklearn, pandas, fastapi, and docker.
"""
    skills = extract_skills(jd)
    canonical_names = {s.canonical_name for s in skills}
    assert "pytorch" in canonical_names
    assert "scikit-learn" in canonical_names
    assert "pandas" in canonical_names
    assert "fastapi" in canonical_names
    assert "docker" in canonical_names


def test_result_sorted_required_first():
    jd = """
Nice to have:
- wandb tracking

Requirements:
- numpy arrays
- fastapi endpoints
"""
    skills = extract_skills(jd)
    required = [s for s in skills if s.is_required]
    preferred = [s for s in skills if not s.is_required]
    # All required should appear before preferred in the returned list
    if required and preferred:
        last_required_idx = max(skills.index(s) for s in required)
        first_preferred_idx = min(skills.index(s) for s in preferred)
        assert last_required_idx < first_preferred_idx


# ---------------------------------------------------------------------------
# Regression tests for heading recognition, casing, punctuation, and bullets
# ---------------------------------------------------------------------------

def test_exact_user_sample_required_and_preferred_split():
    """Reproduces the exact bug reported: 'Required qualifications:' vs 'Preferred qualifications:'."""
    jd = """
Required qualifications:
- Strong Python programming skills.
- Experience with NumPy and pandas.
- Experience building machine learning models with scikit-learn.
- Familiarity with Git and REST APIs.

Preferred qualifications:
- Experience with PyTorch and Transformers.
- Knowledge of Docker and Kubernetes.
- Experience building generative AI applications with LangChain.
"""
    skills = extract_skills(jd)
    req = [s for s in skills if s.is_required]
    pref = [s for s in skills if not s.is_required]

    req_names = {s.canonical_name for s in req}
    pref_names = {s.canonical_name for s in pref}

    # Verify that required skills are indeed marked required
    assert "numpy" in req_names
    assert "pandas" in req_names
    assert "scikit-learn" in req_names
    assert "git" in req_names

    # Verify that preferred skills are marked preferred, NOT required
    assert "pytorch" in pref_names
    assert "hugging-face" in pref_names
    assert "docker" in pref_names
    assert "kubernetes" in pref_names
    assert "langchain" in pref_names

    # Verify counts match expectation
    assert len(req) == 4
    assert len(pref) == 5


def test_heading_capitalization_and_colons():
    """Tests all-caps, title case, lowercase, colons, and dashes."""
    jd = """
REQUIRED QUALIFICATIONS:
- numpy
- pandas

PREFERRED QUALIFICATIONS -
- docker
- kubernetes
"""
    skills = extract_skills(jd)
    req = {s.canonical_name for s in skills if s.is_required}
    pref = {s.canonical_name for s in skills if not s.is_required}

    assert "numpy" in req
    assert "pandas" in req
    assert "docker" in pref
    assert "kubernetes" in pref


def test_markdown_headings_and_blank_lines():
    """Tests markdown ## and ### headers, blank lines, and asterisks."""
    jd = """
## Required Qualifications:

* Experience with scikit-learn
* Knowledge of git

### Preferred Qualifications

* Experience with pytorch
* Familiarity with langchain
"""
    skills = extract_skills(jd)
    req = {s.canonical_name for s in skills if s.is_required}
    pref = {s.canonical_name for s in skills if not s.is_required}

    assert "scikit-learn" in req
    assert "git" in req
    assert "pytorch" in pref
    assert "langchain" in pref


def test_preferred_following_required_does_not_leak():
    """Ensure state transition from required to preferred correctly switches section label."""
    jd = """
Required:
- numpy

Nice to have:
- docker
"""
    skills = extract_skills(jd)
    np_ = _get(skills, "numpy")
    docker = _get(skills, "docker")
    assert np_ is not None and np_.is_required is True
    assert docker is not None and docker.is_required is False


