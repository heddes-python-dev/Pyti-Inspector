import queue
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from telemetry_client import TelemetryClient
from telemetry_receiver import TelemetryReceiver
from pyti_adapter import attach_pyti


class PytiAdapterTests(unittest.TestCase):
    def test_instruments_an_external_pyti_interpreter_without_source_edits(self):
        events = queue.Queue()
        errors = queue.Queue()
        receiver = TelemetryReceiver(
            events.put, lambda _status: None, errors.put, port=0
        )
        receiver.start()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "pyti_app"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            runtime = package / "script_runtime.py"
            runtime.write_text(textwrap.dedent("""
                import sys
                from types import SimpleNamespace

                class BefehlsInterpreter:
                    def __init__(self):
                        self.roboter = SimpleNamespace(
                            x=0, y=0, richtung=1, beeper_im_inventar=0
                        )
                        self.spielfeld_manager = SimpleNamespace(
                            wand_koordinaten=set(),
                            beeper_koordinaten=set(),
                            ziel_position=None,
                        )
                        self.last_execution_error = ""

                    def aktion_ausfuehren(self, name):
                        if name == "moveForward":
                            self.roboter.x += 1
                        if name == "frontClear":
                            return True

                    def interpretiere_und_fuehre_aus(
                        self, text, *, ausfuehren=None, abbruch_event=None
                    ):
                        def call(name):
                            if ausfuehren is not None:
                                return ausfuehren(name)
                            return self.aktion_ausfuehren(name)

                        namespace = {
                            "frontClear": lambda: call("frontClear"),
                            "moveForward": lambda: call("moveForward"),
                        }
                        previous = sys.gettrace()

                        def trace(frame, event, _arg):
                            if frame.f_code.co_filename == "<pyti-script>":
                                return trace
                            return None

                        try:
                            sys.settrace(trace)
                            exec(compile(text, "<pyti-script>", "exec"),
                                 namespace, namespace)
                        except Exception as error:
                            self.last_execution_error = str(error)
                            return False
                        finally:
                            sys.settrace(previous)
                        return True
            """), encoding="utf-8")
            sys.modules.pop("pyti_app.script_runtime", None)
            sys.modules.pop("pyti_app", None)
            restore = attach_pyti(
                root,
                lambda: TelemetryClient(port=receiver.address[1]),
            )
            try:
                from pyti_app.script_runtime import BefehlsInterpreter

                original_path = runtime.read_text(encoding="utf-8")
                interpreter = BefehlsInterpreter()
                self.assertTrue(interpreter.interpretiere_und_fuehre_aus(
                    "steps = 0\n"
                    "clear = frontClear()\n"
                    "moveForward()\n"
                    "steps += 1\n"
                ))
                self.assertEqual(interpreter.roboter.x, 1)
                self.assertEqual(runtime.read_text(encoding="utf-8"), original_path)
                received = []
                while not events.empty():
                    received.append(events.get_nowait())
                kinds = [event["type"] for event in received]
                self.assertIn("session_start", kinds)
                self.assertIn("line", kinds)
                self.assertIn("sensor", kinds)
                self.assertIn("action", kinds)
                self.assertIn("session_end", kinds)
                sensor = next(event for event in received if event["type"] == "sensor")
                self.assertEqual(sensor["result"], True)
                action = next(event for event in received if event["type"] == "action")
                self.assertEqual(action["state"]["x"], 1)
                self.assertEqual(action["variables"]["steps"], 0)
                self.assertFalse(interpreter.interpretiere_und_fuehre_aus(
                    "raise ValueError('script failure')\n"
                ))
                failed_run = []
                while True:
                    event = events.get(timeout=2)
                    failed_run.append(event)
                    if event["type"] == "session_end":
                        break
                failure = next(event for event in failed_run if event["type"] == "error")
                self.assertEqual(failure["line"], 1)
                self.assertIn("script failure", failure["message"])
                self.assertTrue(errors.empty())
                self.assertIsNotNone(BefehlsInterpreter)
            finally:
                restore()
                sys.modules.pop("pyti_app.script_runtime", None)
                sys.modules.pop("pyti_app", None)
                receiver.close()


if __name__ == "__main__":
    unittest.main()
