"""Loopback-only TCP receiver for newline-delimited telemetry events."""

import json
import socketserver
import threading

from telemetry_protocol import validate_event


MAX_EVENT_BYTES = 256 * 1024


class TelemetryReceiver:
    def __init__(self, on_event, on_status, on_error, host="127.0.0.1", port=8765):
        self.on_event = on_event
        self.on_status = on_status
        self.on_error = on_error
        self._server = None
        self._thread = None
        self._host = host
        self._port = port

    @property
    def address(self):
        if self._server is None:
            return self._host, self._port
        return self._server.server_address[:2]

    def start(self):
        receiver = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                receiver.on_status("Sender verbunden")
                try:
                    while True:
                        raw = self.rfile.readline(MAX_EVENT_BYTES + 1)
                        if not raw:
                            break
                        if len(raw) > MAX_EVENT_BYTES:
                            receiver.on_error("Event überschreitet das Größenlimit.")
                            break
                        try:
                            event = validate_event(json.loads(raw))
                        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                            receiver.on_error(f"Ungültiges Telemetrie-Event: {error}")
                            break
                        receiver.on_event(event)
                finally:
                    receiver.on_status("Warte auf Sender")

        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True

        self._server = Server((self._host, self._port), Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="pyti-inspector-receiver",
            daemon=True,
        )
        self._thread.start()

    def close(self):
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)
        self._server = None
        self._thread = None
