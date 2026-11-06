"""Runtime-only Pyti instrumentation; no files in the Pyti project are changed."""

import sys
import threading
import traceback
from functools import wraps
from pathlib import Path

from telemetry_client import TelemetryClient
from pyti_line_tracer import PytiLineTracer
from pyti_telemetry_state import json_value, script_frame, state, variables


SENSORS = {
    "onBeeper",
    "beeperAhead",
    "frontClear",
    "leftClear",
    "rightClear",
    "anyBeeperInBag",
}


def _sandbox_telemetry(interpreter, client_factory):
    client = None

    def close_client():
        nonlocal client
        if client is not None:
            try:
                client.close()
            except OSError:
                pass
            client = None

    def send(event_type, **payload):
        nonlocal client
        if event_type == "session_start":
            close_client()
            try:
                client = client_factory()
                client.connect()
                client.send(
                    "session_start",
                    message=payload.get("message", ""),
                    state=state(interpreter),
                )
            except (OSError, RuntimeError, ValueError) as error:
                close_client()
                print(
                    "Pyti Inspector nicht erreichbar; "
                    f"Pyti läuft ohne Telemetrie: {error}"
                )
                return False
            return True
        if client is None:
            return False
        try:
            if event_type == "line":
                client.send("line", **payload)
            elif event_type == "action":
                client.send(
                    "sensor" if payload["name"] in SENSORS else "action",
                    name=payload["name"],
                    result=json_value(payload.get("result")),
                    **({"line": payload["line"]} if payload.get("line") else {}),
                    state=state(interpreter),
                    variables=payload.get("variables", {}),
                )
            elif event_type == "error":
                client.send(
                    "error",
                    message=payload["message"],
                    traceback=payload.get("traceback", payload["message"]),
                    **({"line": payload["line"]} if payload.get("line") else {}),
                )
            elif event_type == "session_end":
                client.send(
                    "session_end",
                    message=payload.get("message", "Skript beendet"),
                    state=state(interpreter),
                )
        except (OSError, RuntimeError, ValueError, KeyError) as error:
            print(f"Pyti-Inspector-Telemetrie gestoppt: {error}")
            close_client()
            return False
        if event_type == "session_end":
            close_client()
        return True

    return send


def attach_pyti(pyti_root, client_factory=TelemetryClient):
    """Patch the imported interpreter class in memory and return its restore hook."""
    root = Path(pyti_root).resolve()
    if not (root / "pyti_app" / "script_runtime.py").is_file():
        raise FileNotFoundError(f"Not a Pyti source directory: {root}")
    sys.path.insert(0, str(root))
    from pyti_app.script_runtime import BefehlsInterpreter

    original_run = BefehlsInterpreter.interpretiere_und_fuehre_aus
    original_init = BefehlsInterpreter.__init__

    @wraps(original_init)
    def instrumented_init(interpreter, *args, **kwargs):
        original_init(interpreter, *args, **kwargs)
        interpreter.telemetry_handler = _sandbox_telemetry(
            interpreter, client_factory
        )

    def instrumented_run(
        interpreter, script_text, *, ausfuehren=None, abbruch_event=None
    ):
        try:
            client = client_factory()
            client.connect()
        except OSError as error:
            print(f"Pyti Inspector nicht erreichbar; Pyti läuft ohne Telemetrie: {error}")
            return original_run(
                interpreter, script_text,
                ausfuehren=ausfuehren, abbruch_event=abbruch_event,
            )

        line_tracer = None
        last_failure = {}
        real_action = interpreter.aktion_ausfuehren
        telemetry_active = True
        send_lock = threading.Lock()

        def send(event_type, **payload):
            nonlocal telemetry_active
            if not telemetry_active:
                return False
            try:
                with send_lock:
                    client.send(event_type, **payload)
                return True
            except (OSError, RuntimeError, ValueError) as error:
                print(f"Pyti-Inspector-Telemetrie gestoppt: {error}")
                telemetry_active = False
                client.close()
                return False

        def traced_action(name):
            frame = script_frame(sys._getframe(1))
            line = frame.f_lineno if frame else line_tracer.latest_line or None
            action_variables = variables(frame) if frame else dict(
                line_tracer.latest_variables
            )
            if line:
                send("line", line=line, variables=action_variables)
            try:
                result = real_action(name)
            except Exception as error:
                last_failure["message"] = f"{type(error).__name__}: {error}"
                last_failure["traceback"] = traceback.format_exc()
                raise
            event_type = "sensor" if name in SENSORS else "action"
            line_data = {"line": line} if line else {}
            send(
                event_type,
                name=name,
                result=json_value(result),
                **line_data,
                state=state(interpreter),
                variables=action_variables,
            )
            return result

        send(
            "session_start",
            message="Pyti-Skript gestartet",
            state=state(interpreter),
        )
        line_tracer = PytiLineTracer(send)
        line_tracer.install()
        interpreter.aktion_ausfuehren = traced_action
        try:
            success = original_run(
                interpreter,
                script_text,
                ausfuehren=ausfuehren,
                abbruch_event=abbruch_event,
            )
            if not success and not (
                abbruch_event is not None and abbruch_event.is_set()
            ):
                message = (
                    last_failure.get("message")
                    or interpreter.last_execution_error
                    or "Pyti-Skript wurde ohne Erfolg beendet."
                )
                traceback_text = (
                    last_failure.get("traceback")
                    or interpreter.last_execution_error
                    or message
                )
                send(
                    "error",
                    **(
                        {"line": line_tracer.latest_line}
                        if line_tracer.latest_line else {}
                    ),
                    message=message,
                    traceback=traceback_text,
                )
            send(
                "session_end",
                message="Skript erfolgreich beendet" if success else "Skript beendet",
                state=state(interpreter),
            )
            return success
        finally:
            line_tracer.close()
            interpreter.aktion_ausfuehren = real_action
            client.close()

    BefehlsInterpreter.interpretiere_und_fuehre_aus = instrumented_run
    BefehlsInterpreter.__init__ = instrumented_init

    def restore():
        BefehlsInterpreter.interpretiere_und_fuehre_aus = original_run
        BefehlsInterpreter.__init__ = original_init
        if str(root) in sys.path:
            sys.path.remove(str(root))

    return restore
