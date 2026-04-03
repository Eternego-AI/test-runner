"""CLI output — subscribes to test events and prints results as they happen."""

from pathlib import Path

from rich.console import Console

from source.platform.observer import Plan, Event, subscribe

console = Console()

_base_path: str = ""


def _on_plan(signal: Plan):
    if signal.title == "Running directory":
        global _base_path
        _base_path = signal.details.get("path", "")

    elif signal.title == "Running file":
        filepath = signal.details["file"]
        try:
            relative = str(Path(filepath).relative_to(_base_path))
        except ValueError:
            relative = filepath
        console.print(f"\n[bold]{relative}[/bold]")


def _on_event(signal: Event):
    if signal.title == "Test complete":
        result = signal.details["result"]
        status = result["status"]
        title = result["title"][:60]
        time_str = f"{result['time']:.2f}s"

        if status == "pass":
            console.print(f"  [green]v[/green] {title:<60} [dim]{time_str:>7}[/dim] [green]PASS[/green]")
        elif status == "fail":
            console.print(f"  [red]x[/red] {title:<60} [dim]{time_str:>7}[/dim] [red]FAIL[/red]")
        else:
            console.print(f"  [yellow]![/yellow] {title:<60} [dim]{time_str:>7}[/dim] [yellow]ERROR[/yellow]")


def start():
    """Subscribe to events."""
    subscribe(_on_plan, _on_event)


def stop(outcome):
    """Print failures and summary."""
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
