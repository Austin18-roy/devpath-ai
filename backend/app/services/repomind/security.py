import os
from pathlib import Path
from typing import List, Optional, Set, Tuple
from app.services.repomind.models import ScanDiagnostic

DEFAULT_IGNORED_DIRS: Set[str] = {
    ".git",
    ".venv",
    "venv",
    "env",
    "ENV",
    "node_modules",
    ".next",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    "dist",
    "build",
    "site-packages",
    ".eggs",
    ".idea",
    ".vscode",
}


class RepositorySecurityError(ValueError):
    """Raised when repository path validation fails security checks."""
    pass


def get_project_root() -> Path:
    """Returns the canonical root directory of the DevPath AI project."""
    return Path(__file__).resolve().parents[4]


def is_safe_subpath(candidate_path: Path, base_path: Path) -> bool:
    """Check if candidate_path is identical to or within base_path without traversal escape."""
    try:
        candidate_resolved = candidate_path.resolve()
        base_resolved = base_path.resolve()
        return candidate_resolved == base_resolved or base_resolved in candidate_resolved.parents
    except (OSError, RuntimeError):
        return False


def validate_repository_path(
    path_str: str,
    allowed_roots: Optional[List[str]] = None,
    canonical_base: Optional[Path] = None,
) -> Path:
    """
    Validate that path_str points to an existing directory and is within allowed bounds.
    
    Establishes deterministic path resolution:
    - If path_str is absolute: resolves path_str directly.
    - If path_str is relative:
      1. Resolves relative to canonical_base (defaulting to the project root).
      2. If not found at canonical_base, checks canonical_base / 'backend' (supporting
         tests/fixtures paths whether launched from root or backend/).
      3. Otherwise defaults to resolving against canonical_base for deterministic non-existence reporting.
      
    Args:
        path_str: String representation of path.
        allowed_roots: Optional list of directory roots permitted for analysis.
        canonical_base: Optional canonical base directory for resolving relative paths.
        
    Returns:
        Resolved Path object.
        
    Raises:
        RepositorySecurityError: If path does not exist, is not a directory, or fails containment.
    """
    if not path_str or not path_str.strip():
        raise RepositorySecurityError("Repository path cannot be empty.")

    raw_path = Path(path_str).expanduser()
    base = (canonical_base or get_project_root()).resolve()

    try:
        if raw_path.is_absolute():
            resolved_path = raw_path.resolve()
        else:
            # Deterministic resolution relative to project root
            candidate1 = (base / raw_path).resolve()
            candidate2 = (base / "backend" / raw_path).resolve()

            if candidate1.exists():
                resolved_path = candidate1
            elif candidate2.exists():
                resolved_path = candidate2
            else:
                resolved_path = candidate1
    except Exception as exc:
        raise RepositorySecurityError(f"Failed to resolve path: {exc}")

    if not resolved_path.exists():
        raise RepositorySecurityError(f"Repository path does not exist: {resolved_path}")

    if not resolved_path.is_dir():
        raise RepositorySecurityError(f"Repository path is not a directory: {resolved_path}")

    # If allowed_roots are configured, strictly enforce containment
    if allowed_roots:
        resolved_roots = [Path(r).expanduser().resolve() for r in allowed_roots if r.strip()]
        is_allowed = any(is_safe_subpath(resolved_path, root) for root in resolved_roots)
        if not is_allowed:
            raise RepositorySecurityError(
                f"Access denied: {resolved_path} is outside allowed repository roots."
            )

    return resolved_path


def get_scannable_python_files(
    repo_root: Path,
    max_files: int = 1000,
    max_file_size_bytes: int = 1_000_000,
) -> Tuple[List[Path], List[ScanDiagnostic]]:
    """
    Safely find all scannable Python files in repo_root while enforcing safety limits.
    
    Args:
        repo_root: Validated repository root directory.
        max_files: Maximum number of files to scan.
        max_file_size_bytes: Maximum allowed single file size in bytes.
        
    Returns:
        Tuple of (list of valid Python file paths, list of diagnostic warnings/errors).
    """
    python_files: List[Path] = []
    diagnostics: List[ScanDiagnostic] = []

    for root, dirs, files in os.walk(repo_root, topdown=True, followlinks=False):
        # Prune ignored and hidden directories in-place
        dirs[:] = [
            d for d in dirs
            if d not in DEFAULT_IGNORED_DIRS and not d.startswith(".")
        ]

        # Sort files for deterministic scanning order
        for filename in sorted(files):
            if not filename.endswith(".py"):
                continue

            file_path = Path(root) / filename
            rel_path_str = str(file_path.relative_to(repo_root))

            # Symlink guard: check if symlink targets outside repository root
            if file_path.is_symlink():
                try:
                    resolved_symlink = file_path.resolve()
                    if not is_safe_subpath(resolved_symlink, repo_root):
                        diagnostics.append(
                            ScanDiagnostic(
                                file_path=rel_path_str,
                                level="warning",
                                message="Skipped symlink pointing outside repository root.",
                            )
                        )
                        continue
                except (OSError, RuntimeError) as err:
                    diagnostics.append(
                        ScanDiagnostic(
                            file_path=rel_path_str,
                            level="warning",
                            message=f"Skipped unresolvable symlink: {err}",
                        )
                    )
                    continue

            # File size guard
            try:
                file_size = file_path.stat().st_size
                if file_size > max_file_size_bytes:
                    diagnostics.append(
                        ScanDiagnostic(
                            file_path=rel_path_str,
                            level="warning",
                            message=f"Skipped file exceeding maximum size ({file_size} > {max_file_size_bytes} bytes).",
                        )
                    )
                    continue
            except OSError as err:
                diagnostics.append(
                    ScanDiagnostic(
                        file_path=rel_path_str,
                        level="warning",
                        message=f"Could not stat file: {err}",
                    )
                )
                continue

            # Limit total files
            if len(python_files) >= max_files:
                diagnostics.append(
                    ScanDiagnostic(
                        file_path=rel_path_str,
                        level="warning",
                        message=f"Maximum scan limit of {max_files} files reached. Remaining files skipped.",
                    )
                )
                return python_files, diagnostics

            python_files.append(file_path)

    return python_files, diagnostics
