import json
import os
import queue
import time
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from inspector_window import InspectorWindow
from telemetry_client import TelemetryClient
from telemetry_protocol import PROTOCOL_VERSION, validate_event
from telemetry_receiver import TelemetryReceiver


class TelemetryProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_accepts_valid_sensor_event(self):
        event = {
            "version": PROTOCOL_VERSION,
            "type": "sensor",
            "name": "frontClear",
            "result": True,
            "line": 8,
        }
        self.assertIs(validate_event(event), event)

    def test_rejects_unknown_version_or_incomplete_events(self):
        for event in (
            {"version": 2, "type": "line"},
            {"version": PROTOCOL_VERSION, "type": "sensor"},
            {"version": PROTOCOL_VERSION, "type": "error"},
        ):
            with self.subTest(event=event), self.assertRaises(ValueError):
                validate_event(event)

    def test_client_sends_events_to_loopback_receiver(self):
        received = queue.Queue()
        receiver = TelemetryReceiver(
            received.put, lambda _status: None, lambda _error: None, port=0
        )
        receiver.start()
        try:
            with TelemetryClient(port=receiver.address[1]) as client:
                client.send("session_start", message="test")
            event = received.get(timeout=2)
            self.assertEqual(event["type"], "session_start")
            self.assertEqual(event["message"], "test")
            self.assertTrue(event["session_id"])
            json.dumps(event)
        finally:
            receiver.close()

    def test_dashboard_starts_with_loopback_receiver(self):
        window = InspectorWindow()
        try:
            self.assertIn("127.0.0.1:", window.endpoint.text())
            self.assertEqual(window.status.text(), "Warte auf Sender")
            window._show_event({
                "version": PROTOCOL_VERSION,
                "type": "action",
                "name": "moveForward",
                "timestamp": time.time(),
                "line": 4,
                "state": {"x": 2, "y": 1, "direction": "east"},
                "variables": {"step": 3},
            })
            self.assertEqual(window.event_count, 1)
            self.assertEqual(window.command_count, 1)
            variable_names = {
                window.variable_table.item(row, 0).text()
                for row in range(window.variable_table.rowCount())
            }
            self.assertEqual(variable_names, {"x", "y", "direction", "step"})
            window._show_event({
                "version": PROTOCOL_VERSION,
                "type": "sensor",
                "name": "frontClear",
                "result": True,
                "timestamp": time.time(),
            })
            self.assertEqual(window.variable_table.rowCount(), 4)
        finally:
            window.close()

    def test_dashboard_counts_steps_on_both_axes_and_resets_each_session(self):
        window = InspectorWindow()
        try:
            now = time.time()
            window._show_event({
                "type": "session_start",
                "timestamp": now,
                "state": {"x": 1, "y": 2},
            })
            window._show_event({
                "type": "action",
                "name": "moveForward",
                "timestamp": now,
                "state": {"x": 3, "y": 2},
            })
            window._show_event({
                "type": "action",
                "name": "moveForward",
                "timestamp": now,
                "state": {"x": 3, "y": 5},
            })
            self.assertEqual(window.x_steps_label.text(), "X steps: 2")
            self.assertEqual(window.y_steps_label.text(), "Y steps: 3")

            window._show_event({
                "type": "session_start",
                "timestamp": now,
                "state": {"x": 7, "y": 8},
            })
            self.assertEqual(window.x_steps_label.text(), "X steps: 0")
            self.assertEqual(window.y_steps_label.text(), "Y steps: 0")
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
