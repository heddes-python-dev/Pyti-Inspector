"""Send a short simulated Pyti run to the local inspector."""

import time

from telemetry_client import TelemetryClient


def main():
    with TelemetryClient() as client:
        client.send("session_start", message="Demo-Programm gestartet")
        variables = {"x": 0, "y": 0, "visited_states": []}
        client.send("line", line=1, variables=variables)
        client.send("sensor", name="frontClear", result=True, line=2)
        for line, command, x, y in (
            (3, "moveForward", 1, 0),
            (4, "turnLeft", 1, 0),
            (5, "moveForward", 1, 1),
        ):
            variables.update(x=x, y=y)
            variables["visited_states"].append([x, y])
            client.send(
                "action",
                name=command,
                line=line,
                state={"x": x, "y": y, "direction": "south"},
                variables=variables,
            )
            time.sleep(0.7)
        client.send(
            "error",
            line=6,
            message="Demo-Fehler: Beispiel für einen Traceback",
            traceback="Traceback (most recent call last):\n"
            "  File \"demo.py\", line 6, in <module>\n"
            "RuntimeError: Demo-Fehler",
        )
        client.send("session_end", message="Demo beendet")


if __name__ == "__main__":
    main()
