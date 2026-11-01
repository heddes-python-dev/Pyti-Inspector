"""Desktop dashboard for live Pyti telemetry."""

import json
import time
from collections import deque

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from telemetry_receiver import TelemetryReceiver


class UiSignals(QObject):
    event = Signal(dict)
    status = Signal(str)
    error = Signal(str)


class InspectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pyti Inspector")
        self.resize(1100, 720)
        self.signals = UiSignals(self)
        self.signals.event.connect(self._show_event)
        self.signals.status.connect(self._set_status)
        self.signals.error.connect(self._show_error)
        self.started_at = None
        self.event_count = 0
        self.command_count = 0
        self.events = deque(maxlen=1000)
        self.current_variables = {}
        self._build_ui()
        self.receiver = TelemetryReceiver(
            self.signals.event.emit,
            self.signals.status.emit,
            self.signals.error.emit,
        )
        self.receiver.start()
        host, port = self.receiver.address
        self.endpoint.setText(f"Empfang auf {host}:{port} (nur lokal)")

    def _build_ui(self):
        root = QWidget(self)
        layout = QVBoxLayout(root)
        metrics = QHBoxLayout()
        self.status = QLabel("Warte auf Sender")
        self.endpoint = QLabel()
        self.steps = QLabel("Events: 0")
        self.commands = QLabel("Aktionen: 0")
        self.rate = QLabel("Rate: 0.0/s")
        self.elapsed = QLabel("Laufzeit: 0.0 s")
        for label in (
            self.status, self.endpoint, self.steps, self.commands,
            self.rate, self.elapsed,
        ):
            metrics.addWidget(label)
        layout.addLayout(metrics)
        split = QSplitter(root)
        self.event_table = QTableWidget(0, 4, split)
        self.event_table.setHorizontalHeaderLabels(["Zeit", "Typ", "Details", "Zeile"])
        self.event_table.horizontalHeader().setStretchLastSection(True)
        self.event_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.variable_table = QTableWidget(0, 2, split)
        self.variable_table.setHorizontalHeaderLabels(["Variable", "Wert"])
        self.variable_table.horizontalHeader().setStretchLastSection(True)
        split.addWidget(self.event_table)
        split.addWidget(self.variable_table)
        layout.addWidget(split, 1)
        self.traceback = QTextEdit(root)
        self.traceback.setReadOnly(True)
        self.traceback.setPlaceholderText("Fehler und Traceback erscheinen hier.")
        self.traceback.setMaximumHeight(150)
        layout.addWidget(self.traceback)
        self.setCentralWidget(root)

    @Slot(dict)
    def _show_event(self, event):
        self.events.append(event)
        kind = event["type"]
        if kind == "session_start":
            self.started_at = event.get("timestamp", time.time())
            self.command_count = 0
            self.event_count = 0
            self.events.clear()
            self.current_variables.clear()
            self.event_table.setRowCount(0)
            self.traceback.clear()
        self.event_count += 1
        if kind in {"action", "sensor"}:
            self.command_count += 1
        self.steps.setText(f"Events: {self.event_count}")
        self.commands.setText(f"Aktionen/Sensoren: {self.command_count}")
        if self.started_at is not None:
            duration = max(0, time.time() - self.started_at)
            self.elapsed.setText(f"Laufzeit: {duration:.1f} s")
            self.rate.setText(
                f"Rate: {self.command_count / max(duration, 0.1):.1f}/s"
            )
        detail = event.get("name") or event.get("message") or kind
        if "result" in event:
            detail += f" -> {event['result']}"
        if self.event_table.rowCount() >= 1000:
            self.event_table.removeRow(0)
        row = self.event_table.rowCount()
        self.event_table.insertRow(row)
        values = (
            time.strftime("%H:%M:%S", time.localtime(event.get("timestamp", time.time()))),
            kind,
            str(detail),
            str(event.get("line", "")),
        )
        for column, value in enumerate(values):
            self.event_table.setItem(row, column, QTableWidgetItem(value))
        self.event_table.scrollToBottom()
        state = event.get("state", {})
        if "variables" in event:
            self.current_variables = dict(event["variables"])
        elif "variables" in state:
            self.current_variables = dict(state["variables"])
        self.current_variables.update(
            {key: value for key, value in state.items() if key != "variables"}
        )
        if "variables" in event or "variables" in state or state:
            self._show_variables(self.current_variables)
        if kind == "error":
            self.traceback.setPlainText(
                event.get("traceback") or event.get("message", "Unbekannter Fehler")
            )

    def _show_variables(self, variables):
        self.variable_table.setRowCount(len(variables))
        for row, (name, value) in enumerate(sorted(variables.items())):
            self.variable_table.setItem(row, 0, QTableWidgetItem(str(name)))
            self.variable_table.setItem(
                row, 1, QTableWidgetItem(json.dumps(value, ensure_ascii=False))
            )

    @Slot(str)
    def _set_status(self, status):
        self.status.setText(status)

    @Slot(str)
    def _show_error(self, message):
        self.status.setText(message)

    def closeEvent(self, event):
        self.receiver.close()
        super().closeEvent(event)


def run():
    app = QApplication([])
    window = InspectorWindow()
    window.show()
    return app.exec()
