"""CLI output — subscribes to test events and renders live tree output."""

from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.tree import Tree

from source.platform.observer import Plan, Event, subscribe

console = Console()

_files: dict[str, dict] = {}
_base_path: str = ""
_live: Live | None = None


def _on_plan(signal: Plan):
    if signal.title == "Running directory":
        global _base_path
        _base_path = signal.details.get("path", "")

    elif signal.title == "Running file":
        filepath = signal.details["file"]
        _files[filepath] = {"tests": {}, "status": "running"}
        _refresh()

    elif signal.title == "Running test":
        filepath = signal.details.get("file", "")
        test_name = signal.details["test"]
        if filepath in _files:
            title = test_name[5:].replace("_", " ") if test_name.startswith("test_") else test_name
            _files[filepath]["tests"][test_name] = {"status": "running", "time": "", "title": title}
            _refresh()


def _on_event(signal: Event):
    if signal.title == "Test complete":
        filepath = signal.details.get("file", "")
        test_name = signal.details["test"]
        result = signal.details["result"]
        if filepath in _files:
            _files[filepath]["tests"][test_name] = {
                "status": result["status"],
                "time": f"{result['time']:.2f}s",
                "title": result["title"],
            }
            _refresh()

    elif signal.title == "File complete":
        filepath = signal.details["file"]
        if filepath in _files:
            _files[filepath]["status"] = "done"
            _refresh()


def _refresh():
    if _live:
        _live.update(_build_tree())


def _build_tree() -> Tree:
    tree = Tree("", guide_style="dim")

    for filepath, file_data in _files.items():
        try:
            relative = str(Path(filepath).relative_to(_base_path))
        except ValueError:
            relative = filepath

        file_branch = tree.add(f"[bold]{relative}[/bold]")

        for test_data in file_data["tests"].values():
            status = test_data["status"]
            title = test_data["title"][:60]
            time_str = test_data.get("time", "")

            if status == "running":
                line = f"[yellow]→[/yellow] {title}"
            elif status == "pass":
                line = f"[green]✓[/green] {title:<60} [dim]{time_str:>7}[/dim] [green]PASS[/green]"
            elif status == "fail":
                line = f"[red]✗[/red] {title:<60} [dim]{time_str:>7}[/dim] [red]FAIL[/red]"
            else:
                line = f"[yellow]![/yellow] {title:<60} [dim]{time_str:>7}[/dim] [yellow]ERROR[/yellow]"

            file_branch.add(line)

    return tree


def start():
    """Subscribe to events and start live rendering."""
    global _live
    subscribe(_on_plan, _on_event)
    _live = Live(console=console, refresh_per_second=10)
    _live.start()


def stop(outcome):
    """Stop live rendering and print summary."""
    global _live
    if _live:
        _live.stop()
        _live = None

    data = outcome.data or {}
    all_results = data.get("results", {})
    if isinstance(all_results, dict):
        for results_list in all_results.values():
            for result in results_list:
                if result["status"] in ("fail", "error"):
                    console.print(f"\n[red]FAIL[/red] {result['title']}")
                    if result["error"]:
                        console.print(f"  {result['error']}")
                    if result.get("traceback"):
                        console.print(f"  [dim]{result['traceback'].strip()}[/dim]")

    style = "green" if outcome.success else "red"
    console.print(f"\n[{style}]{outcome.message}[/{style}]")
