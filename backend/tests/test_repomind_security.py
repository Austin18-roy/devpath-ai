from pathlib import Path
import pytest
from app.services.repomind.security import (
    RepositorySecurityError,
    get_project_root,
    get_scannable_python_files,
    validate_repository_path,
)

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "sample_repo"


def test_validate_path_success():
    """Verify valid fixture directory resolves cleanly."""
    path = validate_repository_path(str(FIXTURE_ROOT))
    assert path.exists()
    assert path.is_dir()
    assert path == FIXTURE_ROOT.resolve()


def test_validate_relative_path_from_project_root():
    """
    Verify relative path 'backend/tests/fixtures/sample_repo' resolves cleanly
    regardless of working directory.
    """
    allowed = [str(get_project_root())]
    path = validate_repository_path("backend/tests/fixtures/sample_repo", allowed_roots=allowed)
    assert path.exists()
    assert path.is_dir()
    assert path == FIXTURE_ROOT.resolve()


def test_validate_relative_path_from_backend_dir():
    """
    Verify relative path 'tests/fixtures/sample_repo' resolves cleanly
    without duplicate folder prefixes.
    """
    allowed = [str(get_project_root())]
    path = validate_repository_path("tests/fixtures/sample_repo", allowed_roots=allowed)
    assert path.exists()
    assert path.is_dir()
    assert path == FIXTURE_ROOT.resolve()


def test_validate_path_nonexistent():
    """Verify non-existent directory raises security error."""
    with pytest.raises(RepositorySecurityError, match="does not exist"):
        validate_repository_path(str(FIXTURE_ROOT / "non_existent_folder_xyz"))


def test_validate_path_empty():
    """Verify empty path string is rejected."""
    with pytest.raises(RepositorySecurityError, match="cannot be empty"):
        validate_repository_path("")


def test_validate_path_not_a_directory():
    """Verify passing a file path instead of directory is rejected."""
    file_path = FIXTURE_ROOT / "math_utils.py"
    with pytest.raises(RepositorySecurityError, match="not a directory"):
        validate_repository_path(str(file_path))


def test_validate_path_allowed_roots_containment():
    """Verify allowed_roots restricts traversal."""
    allowed = [str(FIXTURE_ROOT)]
    # Subpath or same path is allowed
    assert validate_repository_path(str(FIXTURE_ROOT), allowed_roots=allowed)
    assert validate_repository_path(str(FIXTURE_ROOT / "nested"), allowed_roots=allowed)

    # Outside path is rejected
    outside = FIXTURE_ROOT.parent
    with pytest.raises(RepositorySecurityError, match="outside allowed repository roots"):
        validate_repository_path(str(outside), allowed_roots=allowed)


def test_validate_path_blocks_directory_traversal():
    """Verify path traversal escapes (../../etc) are rejected."""
    allowed = [str(get_project_root())]
    with pytest.raises(RepositorySecurityError):
        validate_repository_path("../../etc", allowed_roots=allowed)


def test_scannable_files_filters_and_limits(tmp_path):
    """Verify ignored directories and file size limits."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "git_hook.py").write_text("print('hidden')")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "pip_module.py").write_text("print('virtualenv')")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "cached.py").write_text("print('cache')")

    valid_file = tmp_path / "valid.py"
    valid_file.write_text("def hello(): pass")

    oversized = tmp_path / "large.py"
    oversized.write_text("a = 1\n" * 1000)

    # Scan with small size limit of 100 bytes
    files, diagnostics = get_scannable_python_files(tmp_path, max_file_size_bytes=100)

    filenames = [f.name for f in files]
    assert "valid.py" in filenames
    assert "git_hook.py" not in filenames
    assert "pip_module.py" not in filenames
    assert "cached.py" not in filenames
    assert "large.py" not in filenames

    # Diagnostic warning should report oversized file
    large_warnings = [d for d in diagnostics if "large.py" in d.file_path]
    assert len(large_warnings) == 1
    assert "exceeding maximum size" in large_warnings[0].message
