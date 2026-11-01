"""Small sender-side client for the Pyti Inspector JSON-lines protocol."""

import json
import socket
import time
import uuid

from telemetry_protocol import PROTOCOL_VERSION, validate_event


class TelemetryClient:
    def __init__(self, host="127.0.0.1", port=8765, timeout=2.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.session_id = str(uuid.uuid4())
        self._socket = None
        self._file = None

    def connect(self):
        if self._socket is not None:
            return
        self._socket = socket.create_connection(
            (self.host, self.port), timeout=self.timeout
        )
        self._file = self._socket.makefile("w", encoding="utf-8")

    def send(self, event_type, **payload):
        if self._socket is None or self._file is None:
            raise RuntimeError("Connect the telemetry client before sending events.")
        event = validate_event({
            "version": PROTOCOL_VERSION,
            "type": event_type,
            "timestamp": time.time(),
            "session_id": self.session_id,
            **payload,
        })
        self._file.write(json.dumps(event, ensure_ascii=False) + "\n")
        self._file.flush()

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_exc_info):
        self.close()
