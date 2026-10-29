import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from app.services.repomind.models import (
    AnalysisResult,
    CodeSymbol,
    DependencyEdge,
    EdgeType,
    ScanDiagnostic,
    SymbolLocation,
    SymbolType,
    UnresolvedCall,
)
from app.services.repomind.security import get_scannable_python_files

STATIC_ANALYSIS_LIMITATIONS: List[str] = [
    "Dynamic dispatch (e.g., calling methods on arbitrary object instances at runtime) cannot be resolved without type inference.",
    "Reflection and dynamic attribute lookups (e.g., getattr, setattr, globals()) are recorded as unresolved calls.",
    "External third-party packages (e.g., standard library, installed pip packages) are tracked as external dependencies rather than expanded into internal AST graphs.",
    "Metaclasses, monkey patching, and decorators altering function signatures are not executed or simulated.",
]

BUILTIN_NAMES: Set[str] = {
    "print", "len", "range", "isinstance", "issubclass", "enumerate", "zip",
    "map", "filter", "list", "dict", "set", "tuple", "str", "int", "float",
    "bool", "bytes", "bytearray", "super", "getattr", "setattr", "hasattr",
    "delattr", "property", "staticmethod", "classmethod", "open", "abs",
    "all", "any", "min", "max", "sum", "sorted", "reversed", "iter", "next",
    "repr", "round", "pow", "divmod", "hash", "id", "callable", "vars", "dir",
    "type", "format", "eval", "exec", "compile", "breakpoint", "help",
}

# Python standard-library module names (top-level). Used to exclude them from
# the imported_packages list so only genuine third-party packages are surfaced.
_STDLIB_TOP_LEVEL: Set[str] = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else {
    "abc", "ast", "asyncio", "builtins", "collections", "concurrent",
    "contextlib", "copy", "csv", "dataclasses", "datetime", "decimal",
    "difflib", "email", "enum", "fileinput", "fnmatch", "fractions",
    "functools", "gc", "glob", "gzip", "hashlib", "heapq", "hmac",
    "html", "http", "importlib", "inspect", "io", "ipaddress", "itertools",
    "json", "keyword", "linecache", "logging", "math", "mimetypes",
    "multiprocessing", "operator", "os", "pathlib", "pickle", "platform",
    "pprint", "queue", "random", "re", "shutil", "signal", "socket",
    "sqlite3", "ssl", "stat", "string", "struct", "subprocess", "sys",
    "tempfile", "textwrap", "threading", "time", "timeit", "tokenize",
    "traceback", "types", "typing", "unittest", "urllib", "uuid",
    "warnings", "weakref", "xml", "xmlrpc", "zipfile", "zlib",
}


def _is_stdlib_module(name: str) -> bool:
    """Return True if `name` is a Python standard-library top-level module."""
    return name in _STDLIB_TOP_LEVEL


def make_symbol_id(symbol_type: SymbolType, file_rel_path: str, qualified_name: str) -> str:
    """Generate a deterministic, stable symbol ID."""
    prefix = {
        SymbolType.MODULE: "module",
        SymbolType.CLASS: "class",
        SymbolType.FUNCTION: "func",
        SymbolType.METHOD: "func",
    }.get(symbol_type, "sym")
    
    if symbol_type == SymbolType.MODULE:
        return f"{prefix}:{file_rel_path}"
    return f"{prefix}:{file_rel_path}::{qualified_name}"


class ModuleImports:
    """Stores resolved and imported symbol references for a single Python file."""
    def __init__(self, file_rel_path: str):
        self.file_rel_path = file_rel_path
        # Maps local name/alias -> (target_module_rel_path, target_symbol_name_or_None)
        self.imported_symbols: Dict[str, Tuple[str, Optional[str]]] = {}
        # Maps local module alias -> target_module_rel_path
        self.imported_modules: Dict[str, str] = {}


class RepoMindASTVisitor(ast.NodeVisitor):
    """
    Static AST visitor for a single Python file.
    Extracts classes, functions, methods, imports, and calls without executing code.
    """
    def __init__(self, file_rel_path: str, repo_files: Set[str]):
        self.file_rel_path = file_rel_path
        self.repo_files = repo_files
        self.symbols: List[CodeSymbol] = []
        self.raw_calls: List[Tuple[str, ast.Call]] = []  # (caller_symbol_id, call_node)
        self.inheritance_targets: List[Tuple[str, str, int]] = []  # (class_id, base_expr_str, lineno)
        self.current_scope: List[str] = []  # Stack of enclosing names (e.g. ['MyClass', 'my_method'])
        self.scope_symbol_ids: List[str] = []  # Stack of enclosing symbol IDs
        self.imports = ModuleImports(file_rel_path)
        self.diagnostics: List[ScanDiagnostic] = []
        # Root package names of external (non-project-local) imports.
        # Used by SkillGraph as one evidence signal. Never executed.
        self.external_imports: Set[str] = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            local_name = alias.asname or alias.name
            target_rel_path = self._resolve_module_path(alias.name)
            if target_rel_path:
                self.imports.imported_modules[local_name] = target_rel_path
            else:
                # External package: record the root package name (first component)
                root_pkg = alias.name.split(".")[0]
                if root_pkg:
                    self.external_imports.add(root_pkg)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        resolved_module = self._resolve_import_from_path(node.module, node.level)
        for alias in node.names:
            local_name = alias.asname or alias.name
            if resolved_module:
                self.imports.imported_symbols[local_name] = (resolved_module, alias.name)
        if not resolved_module and node.module:
            # External package: record the root package name
            root_pkg = node.module.split(".")[0]
            if root_pkg:
                self.external_imports.add(root_pkg)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        class_name = node.name
        qualified_name = ".".join(self.current_scope + [class_name])
        symbol_id = make_symbol_id(SymbolType.CLASS, self.file_rel_path, qualified_name)
        parent_id = self.scope_symbol_ids[-1] if self.scope_symbol_ids else make_symbol_id(SymbolType.MODULE, self.file_rel_path, "")

        symbol = CodeSymbol(
            id=symbol_id,
            name=class_name,
            symbol_type=SymbolType.CLASS,
            location=SymbolLocation(
                file_path=self.file_rel_path,
                start_line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                start_col=getattr(node, "col_offset", 0),
                end_col=getattr(node, "end_col_offset", 0),
            ),
            parent_id=parent_id,
            docstring=ast.get_docstring(node),
        )
        self.symbols.append(symbol)

        # Track inheritance bases
        for base in node.bases:
            base_expr = self._node_to_string(base)
            self.inheritance_targets.append((symbol_id, base_expr, node.lineno))

        self.current_scope.append(class_name)
        self.scope_symbol_ids.append(symbol_id)
        self.generic_visit(node)
        self.scope_symbol_ids.pop()
        self.current_scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._handle_function_node(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._handle_function_node(node)

    def _handle_function_node(self, node):
        func_name = node.name
        is_method = len(self.current_scope) > 0
        sym_type = SymbolType.METHOD if is_method else SymbolType.FUNCTION
        qualified_name = ".".join(self.current_scope + [func_name])
        symbol_id = make_symbol_id(sym_type, self.file_rel_path, qualified_name)
        parent_id = self.scope_symbol_ids[-1] if self.scope_symbol_ids else make_symbol_id(SymbolType.MODULE, self.file_rel_path, "")

        symbol = CodeSymbol(
            id=symbol_id,
            name=func_name,
            symbol_type=sym_type,
            location=SymbolLocation(
                file_path=self.file_rel_path,
                start_line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                start_col=getattr(node, "col_offset", 0),
                end_col=getattr(node, "end_col_offset", 0),
            ),
            parent_id=parent_id,
            docstring=ast.get_docstring(node),
        )
        self.symbols.append(symbol)

        self.current_scope.append(func_name)
        self.scope_symbol_ids.append(symbol_id)
        self.generic_visit(node)
        self.scope_symbol_ids.pop()
        self.current_scope.pop()

    def visit_Call(self, node: ast.Call):
        # Attribute call to enclosing function/method or module
        caller_id = self.scope_symbol_ids[-1] if self.scope_symbol_ids else make_symbol_id(SymbolType.MODULE, self.file_rel_path, "")
        self.raw_calls.append((caller_id, node))
        self.generic_visit(node)

    def _resolve_module_path(self, module_dot_name: str) -> Optional[str]:
        """Convert a dotted module name like 'services.math_utils' to a repository-relative file path."""
        rel_base = module_dot_name.replace(".", "/")
        for candidate in [f"{rel_base}.py", f"{rel_base}/__init__.py"]:
            if candidate in self.repo_files:
                return candidate
        return None

    def _resolve_import_from_path(self, module_name: Optional[str], level: int) -> Optional[str]:
        """Resolve 'from ... import ...' module target to a relative file path."""
        if level > 0:
            # Relative import: compute base directory of current file
            parts = Path(self.file_rel_path).parent.parts
            if level <= len(parts) + 1:
                base_parts = parts[: len(parts) - (level - 1)]
                rel_base = "/".join(base_parts)
                if module_name:
                    rel_base = f"{rel_base}/{module_name.replace('.', '/')}" if rel_base else module_name.replace('.', '/')
                for candidate in [f"{rel_base}.py", f"{rel_base}/__init__.py"]:
                    cleaned = str(Path(candidate))
                    if cleaned in self.repo_files:
                        return cleaned
            return None

        if module_name:
            return self._resolve_module_path(module_name)
        return None

    def _node_to_string(self, node: ast.AST) -> str:
        """Helper to convert simple AST expressions (Name, Attribute) to a string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val_str = self._node_to_string(node.value)
            return f"{val_str}.{node.attr}" if val_str else node.attr
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return ast.dump(node)


class RepoMindParser:
    """
    Orchestrates AST parsing across all files in a repository.
    Produces symbols, resolvable dependency edges, and diagnostics.
    """
    def __init__(self, repo_path: Path, max_files: int = 1000, max_file_size_bytes: int = 1_000_000):
        self.repo_path = repo_path.resolve()
        self.max_files = max_files
        self.max_file_size_bytes = max_file_size_bytes

    def parse_repository(self) -> AnalysisResult:
        files, diagnostics = get_scannable_python_files(
            self.repo_path,
            max_files=self.max_files,
            max_file_size_bytes=self.max_file_size_bytes,
        )

        repo_files_set = {str(f.relative_to(self.repo_path)) for f in files}
        file_visitors: Dict[str, RepoMindASTVisitor] = {}
        all_symbols: List[CodeSymbol] = []
        symbol_map: Dict[str, CodeSymbol] = {}  # symbol_id -> CodeSymbol

        # Pass 1: Parse AST, extract module symbols, classes, functions, imports
        for file_path in files:
            rel_path = str(file_path.relative_to(self.repo_path))

            # Register module symbol
            module_id = make_symbol_id(SymbolType.MODULE, rel_path, "")
            module_symbol = CodeSymbol(
                id=module_id,
                name=file_path.stem,
                symbol_type=SymbolType.MODULE,
                location=SymbolLocation(
                    file_path=rel_path,
                    start_line=1,
                    end_line=1,
                    start_col=0,
                    end_col=0,
                ),
                parent_id=None,
                docstring=None,
            )
            all_symbols.append(module_symbol)
            symbol_map[module_id] = module_symbol

            try:
                content = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError) as err:
                diagnostics.append(
                    ScanDiagnostic(
                        file_path=rel_path,
                        level="error",
                        message=f"Could not read source file: {err}",
                    )
                )
                continue

            try:
                tree = ast.parse(content, filename=rel_path)
            except SyntaxError as err:
                diagnostics.append(
                    ScanDiagnostic(
                        file_path=rel_path,
                        level="error",
                        message=f"Syntax error: {err.msg}",
                        line_number=err.lineno,
                    )
                )
                continue

            visitor = RepoMindASTVisitor(rel_path, repo_files_set)
            visitor.visit(tree)
            file_visitors[rel_path] = visitor

            for sym in visitor.symbols:
                all_symbols.append(sym)
                symbol_map[sym.id] = sym

        # Pass 2: Resolve dependency edges & categorize unresolved calls
        edges: List[DependencyEdge] = []
        unresolved_calls: List[UnresolvedCall] = []

        # Index symbols by file and simple name for resolution
        symbols_by_file_and_name: Dict[Tuple[str, str], List[str]] = {}
        for sym in all_symbols:
            key = (sym.location.file_path, sym.name)
            symbols_by_file_and_name.setdefault(key, []).append(sym.id)

        for rel_path, visitor in file_visitors.items():
            # Resolve class inheritance edges
            for class_id, base_expr, lineno in visitor.inheritance_targets:
                resolved_base_id = self._resolve_expression_symbol(
                    base_expr, rel_path, visitor, symbols_by_file_and_name
                )
                if resolved_base_id and resolved_base_id in symbol_map:
                    edges.append(
                        DependencyEdge(
                            source_id=class_id,
                            target_id=resolved_base_id,
                            edge_type=EdgeType.INHERITS,
                            line_number=lineno,
                        )
                    )

            # Resolve function calls
            for caller_id, call_node in visitor.raw_calls:
                call_expr = visitor._node_to_string(call_node.func)
                lineno = call_node.lineno

                # Check if it's a known Python built-in
                if call_expr in BUILTIN_NAMES:
                    unresolved_calls.append(
                        UnresolvedCall(
                            caller_symbol_id=caller_id,
                            call_expression=call_expr,
                            line_number=lineno,
                            reason="Python standard built-in function (external to repository)",
                        )
                    )
                    continue

                resolved_target_id = self._resolve_call_target(
                    call_node.func, rel_path, visitor, symbols_by_file_and_name, symbol_map, caller_id
                )

                if resolved_target_id:
                    edges.append(
                        DependencyEdge(
                            source_id=caller_id,
                            target_id=resolved_target_id,
                            edge_type=EdgeType.CALLS,
                            line_number=lineno,
                        )
                    )
                else:
                    unresolved_calls.append(
                        UnresolvedCall(
                            caller_symbol_id=caller_id,
                            call_expression=call_expr,
                            line_number=lineno,
                            reason="Dynamic dispatch, external library, or unresolved symbol",
                        )
                    )

        # Sort symbols and edges for deterministic output
        all_symbols.sort(key=lambda s: s.id)
        edges.sort(key=lambda e: (e.source_id, e.target_id, e.line_number))
        unresolved_calls.sort(key=lambda u: (u.caller_symbol_id, u.line_number, u.call_expression))
        diagnostics.sort(key=lambda d: (d.file_path, d.line_number or 0, d.message))

        # Collect external imports across all files; filter out stdlib modules.
        raw_external: Set[str] = set()
        for visitor in file_visitors.values():
            raw_external.update(visitor.external_imports)
        imported_packages = sorted(
            pkg for pkg in raw_external if not _is_stdlib_module(pkg)
        )

        return AnalysisResult(
            repo_path=str(self.repo_path),
            files_scanned=len(files),
            symbols_count=len(all_symbols),
            edges_count=len(edges),
            symbols=all_symbols,
            edges=edges,
            unresolved_calls=unresolved_calls,
            diagnostics=diagnostics,
            limitations=STATIC_ANALYSIS_LIMITATIONS,
            imported_packages=imported_packages,
        )

    def _resolve_call_target(
        self,
        func_node: ast.AST,
        current_file: str,
        visitor: RepoMindASTVisitor,
        symbols_by_file_and_name: Dict[Tuple[str, str], List[str]],
        symbol_map: Dict[str, CodeSymbol],
        caller_id: str,
    ) -> Optional[str]:
        """Attempt to resolve an ast.Call function node to a CodeSymbol ID."""
        # Case 1: Direct name call, e.g. 'helper()' or 'Calculator()'
        if isinstance(func_node, ast.Name):
            name = func_node.id
            # 1a. Defined in current file
            local_matches = symbols_by_file_and_name.get((current_file, name), [])
            # Prefer functions/classes over modules
            func_matches = [m for m in local_matches if not m.startswith("module:")]
            if func_matches:
                return func_matches[0]

            # 1b. Imported symbol from another project file
            if name in visitor.imports.imported_symbols:
                target_file, orig_name = visitor.imports.imported_symbols[name]
                symbol_name = orig_name or name
                remote_matches = symbols_by_file_and_name.get((target_file, symbol_name), [])
                remote_funcs = [m for m in remote_matches if not m.startswith("module:")]
                if remote_funcs:
                    return remote_funcs[0]

            return None

        # Case 2: Attribute call, e.g. 'self.method()', 'module.func()', 'obj.attr()'
        elif isinstance(func_node, ast.Attribute):
            attr_name = func_node.attr

            # 2a. self.method() within a class
            if isinstance(func_node.value, ast.Name) and func_node.value.id == "self":
                caller_sym = symbol_map.get(caller_id)
                if caller_sym:
                    class_id = caller_sym.parent_id if caller_sym.symbol_type == SymbolType.METHOD else caller_id
                    if class_id and class_id in symbol_map:
                        class_sym = symbol_map[class_id]
                        if class_sym.symbol_type == SymbolType.CLASS:
                            expected_id = make_symbol_id(
                                SymbolType.METHOD,
                                current_file,
                                f"{class_sym.name}.{attr_name}",
                            )
                            if expected_id in symbol_map:
                                return expected_id

            # 2b. module.func() where module was imported from repository
            elif isinstance(func_node.value, ast.Name):
                mod_alias = func_node.value.id
                if mod_alias in visitor.imports.imported_modules:
                    target_file = visitor.imports.imported_modules[mod_alias]
                    remote_matches = symbols_by_file_and_name.get((target_file, attr_name), [])
                    remote_funcs = [m for m in remote_matches if not m.startswith("module:")]
                    if remote_funcs:
                        return remote_funcs[0]

        return None

    def _resolve_expression_symbol(
        self,
        expr_str: str,
        current_file: str,
        visitor: RepoMindASTVisitor,
        symbols_by_file_and_name: Dict[Tuple[str, str], List[str]],
    ) -> Optional[str]:
        """Resolve a base class name or expression string."""
        # Simple name: BaseClass
        if "." not in expr_str:
            # Check local file
            local_matches = symbols_by_file_and_name.get((current_file, expr_str), [])
            class_matches = [m for m in local_matches if m.startswith("class:")]
            if class_matches:
                return class_matches[0]

            # Check imported symbols
            if expr_str in visitor.imports.imported_symbols:
                target_file, orig_name = visitor.imports.imported_symbols[expr_str]
                target_name = orig_name or expr_str
                remote_matches = symbols_by_file_and_name.get((target_file, target_name), [])
                class_matches = [m for m in remote_matches if m.startswith("class:")]
                if class_matches:
                    return class_matches[0]

        # Dotted name: module.BaseClass
        else:
            parts = expr_str.split(".", 1)
            mod_alias, class_name = parts[0], parts[1]
            if mod_alias in visitor.imports.imported_modules:
                target_file = visitor.imports.imported_modules[mod_alias]
                remote_matches = symbols_by_file_and_name.get((target_file, class_name), [])
                class_matches = [m for m in remote_matches if m.startswith("class:")]
                if class_matches:
                    return class_matches[0]

        return None
