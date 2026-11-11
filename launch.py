#!/usr/bin/env python3
"""``python launch.py`` from a checkout: the launcher.

The code is ``quantum_study/launch.py``.  Installed (``pip install -e .``), the
same thing is the ``quantum-study`` command.
"""
from quantum_study.launch import main

if __name__ == "__main__":
    raise SystemExit(main())
