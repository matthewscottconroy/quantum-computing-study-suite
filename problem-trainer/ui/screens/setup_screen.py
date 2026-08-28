"""Setup screen — choose mode, topic filter, and items for the session."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QRadioButton, QButtonGroup, QCheckBox, QListWidget, QListWidgetItem,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from problems import all_problems, all_topics
from derivations import all_derivations
from ui import theme

MODE_PROBLEMS    = "problems"
MODE_DERIVATIONS = "derivations"


class SetupScreen(QWidget):
    # emits (mode, [items]) — items are Problem or Derivation objects
    session_started   = pyqtSignal(str, list)
    history_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._topic_cbs: dict[str, QCheckBox] = {}
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 36, 48, 32)
        root.setSpacing(18)

        title = QLabel("Problem Trainer")
        title.setObjectName("heading")
        sub = QLabel(
            "Long-form textbook problems with rubric-based AI grading, and guided "
            "Socratic derivations — Nielsen & Chuang style, across the curriculum."
        )
        sub.setObjectName("subheading")
        sub.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(sub)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        content = QHBoxLayout(); content.setSpacing(28)
        root.addLayout(content, 1)

        # Left column: mode + topic filter
        left = QVBoxLayout(); left.setSpacing(10)

        mode_lbl = QLabel("Mode")
        mode_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        left.addWidget(mode_lbl)

        self._mode_group = QButtonGroup(self)
        self._rb_problems = QRadioButton("Problem Sets — multi-part, rubric-graded")
        self._rb_derivs   = QRadioButton("Guided Derivations — step-by-step Socratic")
        self._rb_problems.setChecked(True)
        for rb in (self._rb_problems, self._rb_derivs):
            self._mode_group.addButton(rb)
            left.addWidget(rb)
        self._rb_problems.toggled.connect(self._on_mode_changed)

        left.addSpacing(10)
        self._topics_lbl = QLabel("Topics")
        self._topics_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        left.addWidget(self._topics_lbl)

        for topic in all_topics():
            cb = QCheckBox(topic)
            cb.setChecked(True)
            color = theme.TOPIC_COLORS.get(topic, theme.ACCENT)
            cb.setStyleSheet(
                f"QCheckBox::indicator:checked {{ background: {color}; border-color: {color}; }}"
            )
            cb.stateChanged.connect(self._refresh_list)
            self._topic_cbs[topic] = cb
            left.addWidget(cb)

        shortcuts = QHBoxLayout()
        for label, val in [("All", True), ("None", False)]:
            btn = QPushButton(label); btn.setObjectName("flat")
            btn.clicked.connect(lambda _, v=val: self._set_all(v))
            shortcuts.addWidget(btn)
        shortcuts.addStretch()
        left.addLayout(shortcuts)

        tip = QLabel(
            "Grading and step-checking use Claude (Anthropic API key required).\n\n"
            "No key? Every part and step still offers “Show model solution” — the "
            "app works fully offline for study."
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
        left.addWidget(tip)
        left.addStretch()
        content.addLayout(left, 2)

        # Right column: item list
        right = QVBoxLayout(); right.setSpacing(8)
        self._list_lbl = QLabel("")
        self._list_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        right.addWidget(self._list_lbl)

        self._list = QListWidget()
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._list.itemSelectionChanged.connect(self._update_start_label)
        self._list.itemDoubleClicked.connect(lambda _item: self._on_start())
        right.addWidget(self._list, 1)

        hint = QLabel("Select one or more (Ctrl/Shift-click). None selected = run all listed.")
        hint.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 11px;")
        right.addWidget(hint)
        content.addLayout(right, 3)

        sep2 = QFrame(); sep2.setObjectName("separator")
        root.addWidget(sep2)

        btn_row = QHBoxLayout()
        history_btn = QPushButton("View History")
        history_btn.setObjectName("flat")
        history_btn.clicked.connect(self.history_requested)
        btn_row.addWidget(history_btn)
        btn_row.addStretch()
        self._start_btn = QPushButton("Start Session")
        self._start_btn.setObjectName("accent")
        self._start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(self._start_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------

    def current_mode(self) -> str:
        return MODE_PROBLEMS if self._rb_problems.isChecked() else MODE_DERIVATIONS

    def _on_mode_changed(self) -> None:
        is_problems = self.current_mode() == MODE_PROBLEMS
        self._topics_lbl.setVisible(is_problems)
        for cb in self._topic_cbs.values():
            cb.setVisible(is_problems)
        self._refresh_list()

    def _set_all(self, val: bool) -> None:
        for cb in self._topic_cbs.values():
            cb.setChecked(val)

    def _selected_topics(self) -> list[str]:
        return [t for t, cb in self._topic_cbs.items() if cb.isChecked()]

    def _refresh_list(self) -> None:
        self._list.clear()
        if self.current_mode() == MODE_PROBLEMS:
            topics = self._selected_topics()
            items = [p for p in all_problems() if p.topic in topics]
            self._list_lbl.setText(f"Problems ({len(items)})")
            for p in items:
                parts = len(p.parts)
                li = QListWidgetItem(f"{p.title}   —   {p.topic}, {parts} parts, "
                                     f"{p.total_points} pts")
                li.setData(Qt.ItemDataRole.UserRole, p)
                self._list.addItem(li)
        else:
            items = all_derivations()
            self._list_lbl.setText(f"Derivations ({len(items)})")
            for d in items:
                li = QListWidgetItem(f"{d.title}   —   {len(d.steps)} steps")
                li.setData(Qt.ItemDataRole.UserRole, d)
                self._list.addItem(li)
        self._update_start_label()

    def _update_start_label(self) -> None:
        n_sel = len(self._list.selectedItems())
        n_all = self._list.count()
        n = n_sel if n_sel else n_all
        noun = "problem" if self.current_mode() == MODE_PROBLEMS else "derivation"
        self._start_btn.setText(f"Start Session ({n} {noun}{'s' if n != 1 else ''})")
        self._start_btn.setEnabled(n > 0)

    def _on_start(self) -> None:
        selected = self._list.selectedItems()
        if selected:
            items = [li.data(Qt.ItemDataRole.UserRole) for li in selected]
        else:
            items = [self._list.item(i).data(Qt.ItemDataRole.UserRole)
                     for i in range(self._list.count())]
        if items:
            self.session_started.emit(self.current_mode(), items)
