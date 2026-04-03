"""Execute — run test functions and capture results."""

import asyncio
import inspect
import time
import traceback


async def run(fn) -> dict:
    """Run a single test function and return the result."""
    name = fn.__name__
    title = (name[5:] if name.startswith("test_") else name).replace("_", " ")
    result = {"title": title, "status": "pass", "error": None, "traceback": None, "time": 0}

    start = time.time()
    try:
        if inspect.iscoroutinefunction(fn):
            await fn()
        else:
            # Sync tests run in a thread so they get their own event loop
            # (they may call asyncio.run() internally)
            await asyncio.to_thread(fn)
    except AssertionError as e:
        result["status"] = "fail"
        result["error"] = str(e) or "Assertion failed"
        result["traceback"] = traceback.format_exc()
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()

    result["time"] = round(time.time() - start, 3)
    return result
