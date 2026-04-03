"""Shell — CLI entry point and terminal output."""

import asyncio
import os
import sys
from pathlib import Path

from source import tester
from shell import cli


async def _run():
    target = sys.argv[1] if len(sys.argv) > 1 else "tests"

    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

    cli.start()

    path = Path(target)
    if path.is_file():
        outcome = await tester.file(str(path))
    else:
        outcome = await tester.directory(str(path))

    cli.stop(outcome)
    return outcome


def main():
    outcome = asyncio.run(_run())
    sys.exit(0 if outcome.success else 1)
