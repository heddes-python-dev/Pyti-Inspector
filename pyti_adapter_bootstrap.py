"""Start Pyti with temporary in-memory inspector instrumentation."""

import sys
from pathlib import Path

from pyti_adapter import attach_pyti


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: pyti_adapter_bootstrap.py /path/to/pyti")
    root = Path(sys.argv[1]).resolve()
    restore = attach_pyti(root)
    try:
        from pyti_app.application import hauptprogramm

        hauptprogramm()
    finally:
        restore()


if __name__ == "__main__":
    main()
