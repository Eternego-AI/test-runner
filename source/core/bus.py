"""Event bus — signal dispatch for test events."""

from source.platform.observer import Plan, Event, send


def propose(title: str, details: dict) -> None:
    send(Plan(title, details))


def broadcast(title: str, details: dict) -> None:
    send(Event(title, details))
