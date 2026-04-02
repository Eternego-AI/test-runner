import tempfile
from pathlib import Path

from test_runner.runner import discover, run


def test_it_discovers_test_files():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "math_test.py").write_text("")
        (Path(d) / "helper.py").write_text("")
        (Path(d) / "string_test.py").write_text("")
        files = discover(d)
        names = [f.name for f in files]
        assert "math_test.py" in names
        assert "string_test.py" in names
        assert "helper.py" not in names


def test_it_discovers_nested_test_files():
    with tempfile.TemporaryDirectory() as d:
        sub = Path(d) / "sub"
        sub.mkdir()
        (sub / "deep_test.py").write_text("")
        files = discover(d)
        assert len(files) == 1
        assert files[0].name == "deep_test.py"


def test_it_runs_passing_tests():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "sample_test.py").write_text(
            "def test_it_works():\n"
            "    assert 1 + 1 == 2\n"
        )
        report = run(d)
        results = list(report.values())[0]
        assert results[0]["status"] == "pass"
        assert results[0]["title"] == "it works"


def test_it_detects_failures():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "fail_test.py").write_text(
            "def test_bad():\n"
            "    assert False, 'nope'\n"
        )
        report = run(d)
        result = list(report.values())[0][0]
        assert result["status"] == "fail"
        assert result["error"] == "nope"


def test_it_detects_errors():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "error_test.py").write_text(
            "def test_boom():\n"
            "    raise RuntimeError('boom')\n"
        )
        report = run(d)
        result = list(report.values())[0][0]
        assert result["status"] == "error"
        assert "RuntimeError: boom" in result["error"]


def test_it_reports_file_level_errors():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "broken_test.py").write_text("raise RuntimeError('broken')\n")
        report = run(d)
        result = list(report.values())[0][0]
        assert result["status"] == "error"
        assert "broken" in result["error"]


def test_it_ignores_non_test_functions():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "mixed_test.py").write_text(
            "def helper():\n"
            "    raise RuntimeError('should not run')\n"
            "\n"
            "def test_real():\n"
            "    assert True\n"
        )
        report = run(d)
        results = list(report.values())[0]
        assert len(results) == 1
        assert results[0]["title"] == "real"


def test_it_runs_tests_in_definition_order():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "order_test.py").write_text(
            "def test_z_last():\n"
            "    pass\n"
            "\n"
            "def test_a_first():\n"
            "    pass\n"
        )
        report = run(d)
        results = list(report.values())[0]
        assert results[0]["title"] == "z last"
        assert results[1]["title"] == "a first"


def test_it_includes_traceback_on_failure():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "tb_test.py").write_text(
            "def test_fails():\n"
            "    x = 1\n"
            "    assert x == 2, 'wrong value'\n"
        )
        report = run(d)
        result = list(report.values())[0][0]
        assert result["traceback"] is not None
        assert "assert x == 2" in result["traceback"]


def test_it_warns_on_empty_test_files():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "empty_test.py").write_text(
            "def helper():\n"
            "    pass\n"
        )
        report = run(d)
        results = list(report.values())[0]
        assert results[0]["status"] == "error"
        assert "No test_" in results[0]["error"]
