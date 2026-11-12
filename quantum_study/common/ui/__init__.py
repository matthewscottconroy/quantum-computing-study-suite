"""Qt-dependent shared code.

Everything in this sub-package imports PyQt6; nothing outside it does, so
``coach.py``, ``dashboard.py`` and ``tools/`` can use :mod:`common` headlessly
on a machine with no Qt at all.

* :mod:`common.ui.theme`          the dark palette and the base stylesheet.
* :mod:`common.ui.widgets`        the small widgets every app reimplemented.
* :mod:`common.ui.reference`      the in-app browser for the ``docs/`` corpus.
* :mod:`common.ui.errata_dialog`  "report this item" -> a GitHub issue.

Import them by module, not from here: ``from common.ui import theme``.  This
file deliberately imports nothing, so a headless tool that touches
``common.ui`` by accident fails with a clear ImportError on the module that
actually needs Qt.
"""
