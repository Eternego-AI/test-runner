"""Discover — find test files and test functions."""

import ast
import importlib.util
import inspect
import sys
from pathlib import Path

from source.platform import filesystem


def test_files(directory: str) -> list[Path]:
    """Find all *_test.py files in the directory, sorted by relative path for consistent output."""
    base = Path(directory)
    files = filesystem.glob_recursive(base, "*_test.py")
    return sorted(files, key=lambda f: str(f.relative_to(base)))


def test_functions(filepath: Path) -> list[tuple[str, callable]]:
    """Load a test file and return (name, function) pairs in definition order."""
    if str(filepath.parent) not in sys.path:
        sys.path.insert(0, str(filepath.parent))

    module_name = str(filepath).replace("/", ".").replace("\\", ".").removesuffix(".py")
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    ordered_names = _definition_order(filepath)
    members = {
        name: fn for name, fn in inspect.getmembers(module)
        if (inspect.isfunction(fn) or inspect.iscoroutinefunction(fn)) and name.startswith("test_")
    }

    return [(name, members[name]) for name in ordered_names if name in members]


def _definition_order(filepath: Path) -> list[str]:
    """Return test_ function names in the order they appear in source."""
    try:
        tree = ast.parse(filesystem.read_text(filepath))
    except SyntaxError:
        return []
    return [
        node.name for node in ast.iter_child_nodes(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    ]
