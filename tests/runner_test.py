import tempfile
from pathlib import Path

from source.core.discover import test_files, test_functions
from source.core.execute import run
from source.platform.observer import Event, subscribe
from source import tester


def test_it_discovers_test_files():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "math_test.py").write_text("")
        (Path(d) / "helper.py").write_text("")
        (Path(d) / "string_test.py").write_text("")
        files = test_files(d)
        names = [f.name for f in files]
        assert "math_test.py" in names
        assert "string_test.py" in names
        assert "helper.py" not in names


def test_it_discovers_nested_test_files():
    with tempfile.TemporaryDirectory() as d:
        sub = Path(d) / "sub"
        sub.mkdir()
        (sub / "deep_test.py").write_text("")
        files = test_files(d)
        assert len(files) == 1
        assert files[0].name == "deep_test.py"


async def test_it_runs_passing_test():
    def passing():
        assert 1 + 1 == 2

    result = await run(passing)
    assert result["status"] == "pass"
    assert result["time"] >= 0


async def test_it_detects_failure():
    def failing():
        assert False, "nope"

    result = await run(failing)
    assert result["status"] == "fail"
    assert result["error"] == "nope"
    assert result["traceback"] is not None


async def test_it_detects_error():
    def erroring():
        raise RuntimeError("boom")

    result = await run(erroring)
    assert result["status"] == "error"
    assert "RuntimeError: boom" in result["error"]


async def test_it_runs_tests_in_definition_order():
    completed = []

    def on_event(signal: Event):
        if signal.title == "Test complete":
            completed.append(signal.details["test"])

    subscribe(on_event)

    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "order_test.py").write_text(
            "def test_z_last():\n"
            "    pass\n\n"
            "def test_a_first():\n"
            "    pass\n"
        )
        await tester.file(str(Path(d) / "order_test.py"))

    # z_last was defined first, so it should complete before a_first
    z_index = next(i for i, name in enumerate(completed) if name == "test_z_last")
    a_index = next(i for i, name in enumerate(completed) if name == "test_a_first")
    assert z_index < a_index


async def test_it_ignores_non_test_functions():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "mixed_test.py").write_text(
            "def helper():\n"
            "    raise RuntimeError('should not run')\n\n"
            "def test_real():\n"
            "    assert True\n"
        )
        outcome = await tester.file(str(Path(d) / "mixed_test.py"))
        results = outcome.data["results"]
        assert len(results) == 1
        assert results[0]["title"] == "real"


async def test_it_warns_on_empty_test_file():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "empty_test.py").write_text(
            "def helper():\n    pass\n"
        )
        outcome = await tester.file(str(Path(d) / "empty_test.py"))
        results = outcome.data["results"]
        assert results[0]["status"] == "error"
        assert "No test_" in results[0]["error"]


async def test_tester_directory_returns_outcome():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "sample_test.py").write_text(
            "def test_works():\n    assert True\n"
        )
        outcome = await tester.directory(d)
        assert outcome.success is True
        assert outcome.data["total"] == 1
        assert outcome.data["passed"] == 1


async def test_tester_test_returns_outcome():
    def my_test():
        assert True

    outcome = await tester.test(my_test)
    assert outcome.success is True
    assert outcome.data["result"]["status"] == "pass"


async def test_async_test_runs_correctly():
    import asyncio
    value = []
    await asyncio.sleep(0.01)
    value.append("done")
    assert value == ["done"]
