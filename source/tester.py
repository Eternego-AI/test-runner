"""Tester — run tests and return outcomes."""

import asyncio
import inspect
from dataclasses import dataclass
from pathlib import Path

from source.core import bus, discover, execute


@dataclass
class Outcome:
    success: bool
    message: str
    data: dict | None = None


async def directory(path: str) -> Outcome:
    """Run all tests in a directory."""
    bus.propose("Running directory", {"path": path})

    files = discover.test_files(path)
    if not files:
        bus.broadcast("Directory complete", {"path": path, "total": 0})
        return Outcome(success=True, message="No test files found.")

    total = passed = failed = errors = 0
    all_results = {}

    for filepath in files:
        file_outcome = await file(str(filepath))
        file_data = file_outcome.data or {}
        all_results[str(filepath)] = file_data.get("results", [])
        total += file_data.get("total", 0)
        passed += file_data.get("passed", 0)
        failed += file_data.get("failed", 0)
        errors += file_data.get("errors", 0)

    success = failed == 0 and errors == 0
    bus.broadcast("Directory complete", {"path": path, "total": total, "passed": passed, "failed": failed, "errors": errors})

    return Outcome(
        success=success,
        message=f"{total} tests: {passed} passed, {failed} failed, {errors} errors",
        data={"results": all_results, "total": total, "passed": passed, "failed": failed, "errors": errors},
    )


async def file(path: str) -> Outcome:
    """Run all tests in a single file."""
    filepath = Path(path)
    bus.propose("Running file", {"file": str(filepath)})

    try:
        functions = discover.test_functions(filepath)
    except Exception as e:
        bus.broadcast("File complete", {"file": str(filepath), "error": str(e)})
        return Outcome(
            success=False,
            message=str(e),
            data={
                "results": [{"title": "(file-level error)", "status": "error", "error": f"{type(e).__name__}: {e}", "traceback": None, "time": 0}],
                "total": 1, "passed": 0, "failed": 0, "errors": 1,
            },
        )

    if not functions:
        bus.broadcast("File complete", {"file": str(filepath), "empty": True})
        return Outcome(
            success=False,
            message="No test_ functions in file",
            data={
                "results": [{"title": "(no tests found)", "status": "error", "error": "No test_ functions in file", "traceback": None, "time": 0}],
                "total": 1, "passed": 0, "failed": 0, "errors": 1,
            },
        )

    results = []
    pending_tasks = []

    for name, fn in functions:
        if inspect.iscoroutinefunction(fn):
            task = asyncio.create_task(test(fn, str(filepath)))
            pending_tasks.append(task)
        else:
            # Sync test — wait for any pending async tasks first? No — let them run.
            # Just run sync immediately, async tasks continue in background.
            outcome = await test(fn, str(filepath))
            results.append(outcome.data["result"])

    # Await all remaining async tasks
    for task in pending_tasks:
        outcome = await task
        results.append(outcome.data["result"])

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    errs = sum(1 for r in results if r["status"] == "error")

    bus.broadcast("File complete", {"file": str(filepath), "total": len(results), "passed": passed, "failed": failed, "errors": errs})

    return Outcome(
        success=failed == 0 and errs == 0,
        message=f"{len(results)} tests: {passed} passed, {failed} failed, {errs} errors",
        data={"results": results, "total": len(results), "passed": passed, "failed": failed, "errors": errs},
    )


async def test(fn, file: str = "") -> Outcome:
    """Run a single test function."""
    bus.propose("Running test", {"file": file, "test": fn.__name__})
    result = await execute.run(fn)
    bus.broadcast("Test complete", {"file": file, "test": fn.__name__, "result": result})

    return Outcome(
        success=result["status"] == "pass",
        message=result["title"],
        data={"result": result},
    )
