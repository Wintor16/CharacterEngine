import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from desktop import theme
from desktop.engine_worker import ReplyWorker

# *Action beats* AND (parenthetical action descriptions) both get a
# dimmer, italic style so they read as clearly distinct from actual
# spoken dialogue -- the model uses both markers roughly interchangeably
# in practice, not just asterisks. Qt's rich text engine doesn't support
# CSS `opacity` on inline spans reliably, so the "transparency" is done
# via an rgba() text color instead (232,232,236 is theme.TEXT_PRIMARY).
# Asterisks are pure markup and get dropped; parentheses are kept since
# they read fine as natural punctuation once styled.
_ACTION_BEAT_RE = re.compile(r"\*([^*]+)\*|\(([^)]+)\)")


def _style_action_beats(text: str) -> str:
    def _replace(match):
        inner = match.group(1) if match.group(1) is not None else f"({match.group(2)})"
        return f'<span style="color: rgba(232,232,236,0.55); font-style: italic;">{inner}</span>'

    return _ACTION_BEAT_RE.sub(_replace, text)


class StatsPanel(QWidget):
    """The extra content shown in the FULL presence state: a live read
    of the relationship/mood state driving her responses."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statsPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(4)

        self._rows = {}
        for key, title in [
            ("mood", "Mood"),
            ("trust", "Trust"),
            ("affection", "Affection"),
            ("respect", "Respect"),
            ("comfort", "Comfort"),
            ("energy", "Energy"),
            ("goal", "Goal"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(6)
            label = QLabel(title)
            label.setObjectName("statusLabel")
            label.setFixedWidth(70)
            value = QLabel("-")
            value.setObjectName("statusLabel")
            value.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 11px;")
            value.setWordWrap(True)
            row.addWidget(label)
            row.addWidget(value, stretch=1)
            layout.addLayout(row)
            self._rows[key] = value

        self.setStyleSheet(theme.PANEL_QSS)

    def refresh(self, state):
        if state is None:
            return
        rel = state.relationship
        self._rows["mood"].setText(state.mood)
        self._rows["trust"].setText(f"{rel.trust:.0f}/100")
        self._rows["affection"].setText(f"{rel.affection:.0f}/100")
        self._rows["respect"].setText(f"{rel.respect:.0f}/100")
        self._rows["comfort"].setText(f"{rel.comfort:.0f}/100")
        self._rows["energy"].setText(f"{state.energy}/100")
        self._rows["goal"].setText(state.current_goal)


class DebugPanel(QWidget):
    """Debug mode (spec §21): structured metadata about the last turn --
    model, timing, the decision/emotion/reasoning that shaped the
    response. Deliberately NOT chain-of-thought text, just labeled
    values, and off by default (toggled from the tray menu)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("debugPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(4)

        header = QLabel("DEBUG")
        header.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 10px; font-weight: 600;")
        layout.addWidget(header)

        self._rows = {}
        for key, title in [
            ("model", "Model"),
            ("timing", "Timing"),
            ("prompt_size", "Prompt"),
            ("decision", "Decision"),
            ("emotion", "Emotion"),
            ("reasoning", "Reasoning"),
            ("plan", "Plan"),
            ("memories", "Memories"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(6)
            label = QLabel(title)
            label.setObjectName("statusLabel")
            label.setFixedWidth(70)
            value = QLabel("-")
            value.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: 10px;")
            value.setWordWrap(True)
            row.addWidget(label)
            row.addWidget(value, stretch=1)
            layout.addLayout(row)
            self._rows[key] = value

        self.setStyleSheet(theme.PANEL_QSS)

    def refresh(self, debug: dict):
        if not debug:
            return
        timing = debug.get("timing", {})
        self._rows["model"].setText(debug.get("model", "-"))
        self._rows["timing"].setText(
            f"brain {timing.get('brain', 0):.2f}s / prompt {timing.get('prompt', 0):.3f}s / "
            f"llm {timing.get('llm', 0):.2f}s / total {timing.get('total', 0):.2f}s"
        )
        self._rows["prompt_size"].setText(f"{debug.get('prompt_chars', 0):,} chars")
        self._rows["decision"].setText(f"{debug.get('decision_intent', '-')} ({debug.get('decision_reason', '')})")
        self._rows["emotion"].setText(f"{debug.get('emotion', '-')} ({debug.get('emotion_intensity', 0)})")
        self._rows["reasoning"].setText(debug.get("reasoning_objective", "-"))
        self._rows["plan"].setText(f"{debug.get('plan_tone', '-')}, {debug.get('plan_length', '-')}")
        self._rows["memories"].setText(str(debug.get("memories_used", 0)))


class ChatPanel(QWidget):
    """The COMPACT/FULL presence states: header + message log + input,
    with an optional stats panel (FULL) toggled from the header."""

    minimize_requested = Signal()
    expand_toggled = Signal(bool)
    busy_changed = Signal(bool)

    def __init__(self, engine, display_name: str, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._worker = None
        self._last_mood = "neutral"
        self._expanded = False
        self._debug_enabled = False
        self.setObjectName("chatPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {theme.mood_color('neutral')}; font-size: 12px;")

        name_col = QVBoxLayout()
        name_col.setSpacing(0)
        self.name_label = QLabel(display_name)
        self.name_label.setObjectName("nameLabel")
        self.status_label = QLabel("neutral")
        self.status_label.setObjectName("statusLabel")
        name_col.addWidget(self.name_label)
        name_col.addWidget(self.status_label)

        header.addWidget(self.status_dot)
        header.addLayout(name_col)
        header.addStretch()

        self.expand_button = QPushButton("⤢")
        self.expand_button.setObjectName("headerButton")
        self.expand_button.setFixedSize(24, 24)
        self.expand_button.setCursor(Qt.PointingHandCursor)
        self.expand_button.setToolTip("Show relationship/mood details")
        self.expand_button.clicked.connect(self._toggle_expanded)
        header.addWidget(self.expand_button)

        self.minimize_button = QPushButton("—")
        self.minimize_button.setObjectName("headerButton")
        self.minimize_button.setFixedSize(24, 24)
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.clicked.connect(self.minimize_requested.emit)
        header.addWidget(self.minimize_button)

        layout.addLayout(header)

        self.stats_panel = StatsPanel()
        self.stats_panel.hide()
        layout.addWidget(self.stats_panel)

        self.debug_panel = DebugPanel()
        self.debug_panel.hide()
        layout.addWidget(self.debug_panel)

        self.chat_log = QTextEdit()
        self.chat_log.setObjectName("chatLog")
        self.chat_log.setReadOnly(True)
        self.chat_log.setFrameStyle(QTextEdit.NoFrame)
        layout.addWidget(self.chat_log, stretch=1)

        input_row = QHBoxLayout()
        input_row.setSpacing(6)
        self.input_box = QLineEdit()
        self.input_box.setObjectName("inputBox")
        self.input_box.setPlaceholderText("Message Kurumi...")
        self.input_box.returnPressed.connect(self._send)
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("sendButton")
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.clicked.connect(self._send)
        input_row.addWidget(self.input_box, stretch=1)
        input_row.addWidget(self.send_button)
        layout.addLayout(input_row)

        self.setStyleSheet(theme.PANEL_QSS)

    def focus_input(self):
        self.input_box.setFocus()

    def greet(self, text: str):
        self._append("Kurumi", text, theme.ACCENT)

    def set_debug_enabled(self, enabled: bool):
        self._debug_enabled = enabled
        visible = enabled and self._expanded
        self.debug_panel.setVisible(visible)
        if visible:
            self.debug_panel.refresh(self.engine.last_debug)

    def _toggle_expanded(self):
        self._expanded = not self._expanded
        self.stats_panel.setVisible(self._expanded)
        if self._expanded:
            self.stats_panel.refresh(getattr(self.engine.brain, "state", None))
        self.debug_panel.setVisible(self._expanded and self._debug_enabled)
        if self._expanded and self._debug_enabled:
            self.debug_panel.refresh(self.engine.last_debug)
        self.expand_button.setText("⤡" if self._expanded else "⤢")
        self.expand_toggled.emit(self._expanded)

    def _append(self, sender: str, text: str, color: str):
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe = _style_action_beats(safe).replace("\n", "<br>")
        self.chat_log.append(
            f'<div style="margin-bottom:10px;">'
            f'<span style="color:{color}; font-weight:600; font-size:11px;">{sender}</span><br>'
            f'<span style="color:{theme.TEXT_PRIMARY};">{safe}</span>'
            f"</div>"
        )
        self.chat_log.moveCursor(QTextCursor.End)

    def _set_busy(self, busy: bool):
        self.input_box.setEnabled(not busy)
        self.send_button.setEnabled(not busy)
        self.status_label.setText("thinking..." if busy else self._last_mood)
        self.busy_changed.emit(busy)

    def _send(self):
        text = self.input_box.text().strip()
        if not text or self._worker is not None:
            return
        self.input_box.clear()
        self._append("You", text, theme.TEXT_SECONDARY)
        self._set_busy(True)

        self._worker = ReplyWorker(self.engine, text, self)
        self._worker.succeeded.connect(self._on_success)
        self._worker.failed.connect(self._on_failure)
        self._worker.finished.connect(self._cleanup_worker)
        self._worker.start()

    def _on_success(self, response):
        self._append("Kurumi", response.text, theme.ACCENT)
        state = getattr(self.engine.brain, "state", None)
        self._last_mood = state.mood if state is not None else "neutral"
        self.status_dot.setStyleSheet(f"color: {theme.mood_color(self._last_mood)}; font-size: 12px;")
        if self._expanded:
            self.stats_panel.refresh(state)
            if self._debug_enabled:
                self.debug_panel.refresh(self.engine.last_debug)

    def _on_failure(self, error: str):
        self._append("System", f"*A disturbance in time...* ({error})", theme.TEXT_MUTED)

    def _cleanup_worker(self):
        self._set_busy(False)
        self._worker = None
