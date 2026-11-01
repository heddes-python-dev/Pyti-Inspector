"""Wrap Pyti's existing trace callback to publish learner-script line events."""

import sys
import threading

from pyti_telemetry_state import variables


class PytiLineTracer:
    def __init__(self, send):
        self.send = send
        self.latest_line = 0
        self.latest_variables = {}
        self._thread = threading.get_ident()
        self._real_settrace = sys.settrace

    def install(self):
        sys.settrace = self._settrace

    def close(self):
        sys.settrace = self._real_settrace

    def _settrace(self, trace_function):
        if threading.get_ident() != self._thread or trace_function is None:
            return self._real_settrace(trace_function)

        def wrap_local(local_trace):
            if local_trace is None:
                return None

            def dispatch(frame, event, arg):
                next_trace = local_trace(frame, event, arg)
                if frame.f_code.co_filename == "<pyti-script>" and event == "line":
                    self.latest_line = frame.f_lineno
                    self.latest_variables = variables(frame)
                    self.send(
                        "line",
                        line=self.latest_line,
                        variables=self.latest_variables,
                    )
                return wrap_local(next_trace)

            return dispatch

        def dispatch_global(frame, event, arg):
            return wrap_local(trace_function(frame, event, arg))

        return self._real_settrace(dispatch_global)
