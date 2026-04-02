import ast
import asyncio
import importlib.util
import inspect
import sys
import traceback
from pathlib import Path


def discover(directory):
    return sorted(Path(directory).rglob("*_test.py"))


def _definition_order(filepath):
    """Return test_ function names in the order they appear in source."""
    try:
        tree = ast.parse(filepath.read_text())
    except SyntaxError:
        return []
    return [
        node.name for node in ast.iter_child_nodes(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    ]


def run(directory):
    files = discover(directory)
    report = {}

    for filepath in files:
        if str(filepath.parent) not in sys.path:
            sys.path.insert(0, str(filepath.parent))
        module_name = str(filepath).replace("/", ".").replace("\\", ".").removesuffix(".py")
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            tb = traceback.format_exc()
            report[str(filepath)] = [
                {"title": "(file-level error)", "status": "error", "error": f"{type(e).__name__}: {e}", "traceback": tb}
            ]
            continue

        ordered_names = _definition_order(filepath)
        def is_test(obj):
            return (inspect.isfunction(obj) or inspect.iscoroutinefunction(obj)) and obj.__name__.startswith("test_")
        functions = {name: fn for name, fn in inspect.getmembers(module, is_test)}

        if not functions:
            report[str(filepath)] = [
                {"title": "(no tests found)", "status": "error", "error": "No test_ functions in file", "traceback": None}
            ]
            continue

        results = []
        for name in ordered_names:
            fn = functions.get(name)
            if not fn:
                continue
            title = name[5:].replace("_", " ")
            result = {"title": title, "status": "pass", "error": None, "traceback": None}
            try:
                if asyncio.iscoroutinefunction(fn):
                    asyncio.run(fn())
                else:
                    fn()
            except AssertionError as e:
                result["status"] = "fail"
                result["error"] = str(e) or "Assertion failed"
                result["traceback"] = traceback.format_exc()
            except Exception as e:
                result["status"] = "error"
                result["error"] = f"{type(e).__name__}: {e}"
                result["traceback"] = traceback.format_exc()
            results.append(result)

        report[str(filepath)] = results

    return report
