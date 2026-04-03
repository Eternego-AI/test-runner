import sys
from pathlib import Path
from .runner import run


PASS = "\033[32m PASS \033[0m"
FAIL = "\033[31m FAIL \033[0m"
ERROR = "\033[33m ERROR \033[0m"
DIM = "\033[2m"
RESET = "\033[0m"

STATUS = {"pass": PASS, "fail": FAIL, "error": ERROR}


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "tests"
    report = run(directory)
    base = Path(directory)

    total = 0
    passed = 0
    failed = 0
    errors = 0
    failures = []

    # Group files by parent directory
    grouped = {}
    for filepath, results in report.items():
        relative = Path(filepath).relative_to(base)
        group = str(relative.parent) if relative.parent != Path(".") else ""
        grouped.setdefault(group, []).append((relative.name, results))

    for group in sorted(grouped):
        if group:
            print(f"\n{group}/")
        for filename, results in sorted(grouped[group]):
            indent = "  " if group else ""
            print(f"{indent}{filename}")
            for result in results:
                label = STATUS[result["status"]]
                print(f"{indent}  {label} {result['title']}")
                total += 1
                if result["status"] == "pass":
                    passed += 1
                elif result["status"] == "fail":
                    failed += 1
                    failures.append(result)
                else:
                    errors += 1
                    failures.append(result)

    if failures:
        print(f"\n{'-' * 60}")
        for result in failures:
            print(f"\n{FAIL} {result['title']}")
            if result["error"]:
                print(f"  {result['error']}")
            if result.get("traceback"):
                for line in result["traceback"].strip().splitlines():
                    print(f"  {DIM}{line}{RESET}")

    print(f"\n{total} tests: {passed} passed, {failed} failed, {errors} errors")
    sys.exit(1 if failed or errors else 0)


main()
