# Test Runner

Minimal Python test runner. No framework imports. No decorators. Just functions and `assert`.

## Philosophy

- Tests are plain Python — `def test_*` or `async def test_*`
- Zero imports from the runner in test files
- `def` tests run sequentially, `async def` tests run concurrently
- The runner is a tool, not a dependency of your project

## Install

```bash
pip install git+https://github.com/Eternego-AI/test-runner.git
```

Update:

```bash
pip install --upgrade git+https://github.com/Eternego-AI/test-runner.git
```

## Usage

Write tests:

```python
# tests/math_test.py

def test_addition():
    assert 1 + 1 == 2

async def test_fetch():
    result = await fetch("/api")
    assert result.status == 200
```

Run:

```bash
test-runner
test-runner tests/core
test-runner tests/math_test.py
```

## Sync vs Async

`def` tests run one at a time, in definition order. Use for tests that share state.

`async def` tests run concurrently. Use for independent tests.

```python
# Sequential — shares state
def test_create():
    setup_db()
    assert db.count() == 1

def test_verify():
    assert db.count() == 1

# Concurrent — independent
async def test_users():
    assert await fetch("/users")

async def test_posts():
    assert await fetch("/posts")
```

## Features

- Discovers `*_test.py` files recursively
- Runs `test_*` functions in definition order
- `def`: sequential, `async def`: concurrent
- Live tree output with execution time
- Tracebacks on failure
- Event-driven — subscribe to signals for custom output
- Usable as a CLI tool or as a library

## As a Library

```python
from source import tester

outcome = await tester.directory("tests")
print(outcome.success)   # True/False
print(outcome.message)   # "305 tests: 305 passed, 0 failed, 0 errors"

outcome = await tester.file("tests/math_test.py")
outcome = await tester.test(my_function)
```

## Custom Output

```python
from source.platform.observer import Event, subscribe

def on_complete(signal: Event):
    if signal.title == "Test complete":
        r = signal.details["result"]
        print(f"{r['title']}: {r['status']} ({r['time']}s)")

subscribe(on_complete)
```

## Architecture

```
source/
  tester.py        — business: directory(), file(), test() -> Outcome
  cli.py           — entry point for test-runner command
  core/
    discover.py    — find test files and functions
    execute.py     — run function, capture result and time
    bus.py         — signal dispatch
  platform/
    observer.py    — event subscription system
    filesystem.py  — file discovery
shell/
  cli.py           — live terminal output via rich
```

## License

MIT
