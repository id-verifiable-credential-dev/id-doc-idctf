"""Unit tests for the Ask IDCTF function and scripts.

Run: .venv/bin/python -m unittest discover -s tests -t . -v
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
for folder in ("api", "scripts"):
    path = str(ROOT / folder)
    if path not in sys.path:
        sys.path.insert(0, path)
