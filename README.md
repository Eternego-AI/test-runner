# Test Runner

Minimal Python test runner. Discovers files, runs functions, reports results.

## Philosophy

- Tests are plain Python — just functions and `assert`
- Zero imports from the runner in test files
- Any `test_*` function in any `*_test.py` file is a test
- The runner is a tool, not a dependency of your project

## Installation

Download the latest release for your OS from [Releases](https://github.com/Eternego-AI/test-runner/releases).

### Linux / macOS

```bash
curl -sL https://github.com/Eternego-AI/test-runner/releases/latest/download/test-runner-linux.zip -o test-runner.zip
unzip -qo test-runner.zip -d /tmp/test-runner
```

#### or macOS:

```bash
curl -sL https://github.com/Eternego-AI/test-runner/releases/latest/download/test-runner-macos.zip -o test-runner.zip
unzip -qo test-runner.zip -d /tmp/test-runner
```

### Windows

```powershell
Invoke-WebRequest https://github.com/Eternego-AI/test-runner/releases/latest/download/test-runner-windows.zip -OutFile test-runner.zip
Expand-Archive -Path test-runner.zip -DestinationPath $env:TEMP\test-runner -Force
```

## Usage

Write tests as plain Python files:

```python
# tests/math_test.py

def test_addition():
    assert 1 + 1 == 2

def test_strings():
    assert "hello".upper() == "HELLO"
```

Run them:

### Linux / macOS

```bash
PYTHONPATH="/tmp/test-runner:." python -m test_runner tests
```

### Windows

```powershell
$env:PYTHONPATH = "$env:TEMP\test-runner;."
python -m test_runner tests
```

## Features

- Discovers `*_test.py` files recursively
- Runs `test_*` functions in definition order
- Supports `async def test_*` functions
- Groups output by directory
- Shows tracebacks on failure
- Warns on empty test files (no `test_*` functions)

## Output

```
math/
  arithmetic_test.py
    PASS  addition works
    PASS  subtraction works
  string_test.py
    PASS  uppercase
    FAIL  lowercase
           Expected 'hello', got 'HELLO'

4 tests: 3 passed, 1 failed, 0 errors
```

## License

MIT
