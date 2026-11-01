"""Versioned JSON-lines protocol shared by senders and the inspector."""

from typing import Any


PROTOCOL_VERSION = 1
EVENT_TYPES = {
    "session_start",
    "line",
    "action",
    "sensor",
    "state",
    "error",
    "session_end",
}


def validate_event(event: Any) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise ValueError("An event must be a JSON object.")
    if event.get("version") != PROTOCOL_VERSION:
        raise ValueError(f"Unsupported protocol version: {event.get('version')!r}")
    event_type = event.get("type")
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unsupported event type: {event_type!r}")
    if "timestamp" in event and not isinstance(event["timestamp"], (int, float)):
        raise ValueError("timestamp must be a number.")
    if "line" in event and (
        not isinstance(event["line"], int) or event["line"] < 1
    ):
        raise ValueError("line must be a positive integer.")
    for key in ("name", "message", "session_id"):
        if key in event and not isinstance(event[key], str):
            raise ValueError(f"{key} must be a string.")
    for key in ("variables", "state"):
        if key in event and not isinstance(event[key], dict):
            raise ValueError(f"{key} must be a JSON object.")
    if "state" in event and "variables" in event["state"] and not isinstance(
        event["state"]["variables"], dict
    ):
        raise ValueError("state.variables must be a JSON object.")
    if event_type in {"action", "sensor"} and not isinstance(
        event.get("name"), str
    ):
        raise ValueError(f"{event_type} events require a name.")
    if event_type == "error" and not isinstance(event.get("message"), str):
        raise ValueError("error events require a message.")
    return event
