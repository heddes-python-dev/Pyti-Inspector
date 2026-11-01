"""Launch the standalone inspector and Pyti with runtime-only telemetry."""

import argparse
import socket
import subprocess
import sys
import time
from pathlib import Path


INSPECTOR_ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765


def _wait_for_inspector(process, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("The Pyti Inspector exited before it started listening.")
        try:
            with socket.create_connection((HOST, PORT), timeout=0.2):
                return
        except OSError:
            time.sleep(0.1)
    raise TimeoutError(f"The Pyti Inspector did not listen on {HOST}:{PORT}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pyti_directory",
        type=Path,
        help="Path to the unchanged pyti_lernprogramm source directory",
    )
    args = parser.parse_args()
    pyti_root = args.pyti_directory.expanduser().resolve()
    if not (pyti_root / "main.py").is_file():
        parser.error(f"No Pyti main.py found in {pyti_root}")

    inspector = subprocess.Popen([sys.executable, str(INSPECTOR_ROOT / "main.py")])
    try:
        _wait_for_inspector(inspector)
        return subprocess.call(
            [
                sys.executable,
                str(INSPECTOR_ROOT / "pyti_adapter_bootstrap.py"),
                str(pyti_root),
            ],
            cwd=pyti_root,
        )
    finally:
        if inspector.poll() is None:
            inspector.terminate()
            try:
                inspector.wait(timeout=5)
            except subprocess.TimeoutExpired:
                inspector.kill()
                inspector.wait()


if __name__ == "__main__":
    raise SystemExit(main())
