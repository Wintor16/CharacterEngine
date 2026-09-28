from pathlib import Path

from PySide6.QtCore import QPoint, QSettings, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from desktop import theme
from desktop.chat_panel import ChatPanel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ICON_PATH = PROJECT_ROOT / "icon.png"

AVATAR_SIZE = 64
COMPACT_SIZE = QSize(360, 480)
FULL_SIZE = QSize(420, 640)
SCREEN_MARGIN = 24
NOTIFICATION_DURATION_MS = 8000


class NotificationBubble(QWidget):
    """The NOTIFICATION presence state: a small, non-intrusive popup that
    appears near the avatar, auto-dismisses, and opens the chat on click.
    A separate top-level widget rather than a FloatingWindow mode, since
    it needs to sit beside the avatar without replacing it."""

    def __init__(self, text: str, on_click, duration_ms: int = NOTIFICATION_DURATION_MS):
        super().__init__()
        self._on_click = on_click

        # A second WA_TranslucentBackground + custom-paintEvent top-level
        # widget (the same recipe FloatingWindow itself uses) did not
        # composite at all under this XWayland setup -- confirmed with a
        # minimal repro, a plain QSS-styled opaque widget rendered fine.
        # Traded rounded outer corners for content that reliably shows up.
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        bg = theme.PANEL_BG
        self.setStyleSheet(
            f"background-color: rgb({bg[0]}, {bg[1]}, {bg[2]});"
            f"border: 1px solid {theme.ACCENT};"
            f"border-radius: 10px;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {theme.TEXT_PRIMARY}; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(label)

        self.setFixedWidth(240)
        self.adjustSize()

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close)
        self._timer.start(duration_ms)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._on_click:
            self._on_click()
        self.close()


class FloatingWindow(QWidget):
    """A persistent, always-on-top presence with several states:
    MINIMIZED (a small circular avatar you can drag anywhere), COMPACT
    (a chat panel), FULL (chat + a live relationship/mood readout), and
    NOTIFICATION (a separate small popup, see NotificationBubble). Click
    the avatar to open the chat; click "-" to collapse back to it."""

    def __init__(self, engine, display_name: str):
        super().__init__()
        self._mode = "avatar"
        self._full = False
        self._busy = False
        self._hovered = False
        self._drag_pos = None
        self._drag_moved = False
        self._notification = None

        self._settings = QSettings("KurumiAI", "DesktopUI")
        self._avatar_pixmap = QPixmap(str(ICON_PATH)) if ICON_PATH.exists() else None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_Hover, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.chat_panel = ChatPanel(engine, display_name, self)
        self.chat_panel.minimize_requested.connect(self.show_avatar)
        self.chat_panel.expand_toggled.connect(self._on_expand_toggled)
        self.chat_panel.busy_changed.connect(self.set_busy)
        layout.addWidget(self.chat_panel)

        self._restore_avatar_position()
        self.show_avatar()

    # ------------------------------------------------------------------
    # Presence state
    # ------------------------------------------------------------------

    def show_avatar(self):
        self._mode = "avatar"
        self.chat_panel.hide()
        self.setFixedSize(AVATAR_SIZE, AVATAR_SIZE)
        self._clamp_to_screen()
        self.update()

    def show_compact(self):
        self._mode = "compact"
        self.setFixedSize(FULL_SIZE if self._full else COMPACT_SIZE)
        self._clamp_to_screen()
        self.chat_panel.show()
        self.chat_panel.focus_input()
        self.update()

    def _on_expand_toggled(self, expanded: bool):
        self._full = expanded
        if self._mode != "avatar":
            self.setFixedSize(FULL_SIZE if expanded else COMPACT_SIZE)
            self._clamp_to_screen()

    def set_busy(self, busy: bool):
        """ACTIVE indicator: highlights the avatar ring while a reply is
        generating, even if the chat panel isn't the visible surface
        (e.g. minimized right after sending, or a future proactive
        message being composed)."""
        self._busy = busy
        self.update()

    def show_notification(self, text: str):
        """NOTIFICATION presence state. Only meaningful while minimized --
        if the chat is already open, just deliver the line into it."""
        if self._mode != "avatar":
            self.chat_panel.greet(text)
            return

        if self._notification is not None:
            self._notification.close()

        bubble = NotificationBubble(text, on_click=lambda: self._open_from_notification(text))
        x, y = self.x(), self.y() - bubble.height() - 8
        screen = QApplication.primaryScreen()
        if screen is not None:
            avail = screen.availableGeometry()
            x = min(max(x, avail.left()), avail.right() - bubble.width())
            if y < avail.top():
                y = self.y() + AVATAR_SIZE + 8
        bubble.move(x, y)
        bubble.show()
        bubble.raise_()
        self._notification = bubble

    def _open_from_notification(self, text: str):
        self.show_compact()
        self.chat_panel.greet(text)
        self._notification = None

    def _clamp_to_screen(self):
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        avail = screen.availableGeometry()
        geo = self.geometry()
        x = min(max(geo.x(), avail.left()), avail.right() - geo.width())
        y = min(max(geo.y(), avail.top()), avail.bottom() - geo.height())
        self.move(x, y)

    def _restore_avatar_position(self):
        saved = self._settings.value("avatar_pos")
        if isinstance(saved, QPoint):
            self.move(saved)
            return
        screen = QApplication.primaryScreen()
        if screen is not None:
            avail = screen.availableGeometry()
            self.move(
                avail.right() - AVATAR_SIZE - SCREEN_MARGIN,
                avail.bottom() - AVATAR_SIZE - SCREEN_MARGIN,
            )

    def closeEvent(self, event):
        if self._mode == "avatar":
            self._settings.setValue("avatar_pos", self.pos())
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # Dragging (avatar mode) + click-to-open + hover glow
    # ------------------------------------------------------------------

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._mode == "avatar":
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            self._drag_moved = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._mode == "avatar" and self._drag_pos is not None and (event.buttons() & Qt.LeftButton):
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            if (new_pos - self.pos()).manhattanLength() > 3:
                self._drag_moved = True
            self.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._mode == "avatar":
            if not self._drag_moved:
                self._settings.setValue("avatar_pos", self.pos())
                self.show_compact()
            else:
                self._settings.setValue("avatar_pos", self.pos())
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self._mode == "avatar":
            self._paint_avatar(painter)
        else:
            self._paint_panel(painter)
        painter.end()

    def _paint_avatar(self, painter: QPainter):
        size = AVATAR_SIZE
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(*theme.PANEL_BG))
        painter.drawEllipse(0, 0, size, size)

        if self._avatar_pixmap and not self._avatar_pixmap.isNull():
            inset = 3
            path = QPainterPath()
            path.addEllipse(inset, inset, size - inset * 2, size - inset * 2)
            painter.save()
            painter.setClipPath(path)
            inner = size - inset * 2
            scaled = self._avatar_pixmap.scaled(
                inner, inner, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = inset - (scaled.width() - inner) // 2
            y = inset - (scaled.height() - inner) // 2
            painter.drawPixmap(x, y, scaled)
            painter.restore()

        highlighted = self._busy or self._hovered
        ring = QPen(QColor(theme.ACCENT if highlighted else theme.PANEL_BORDER))
        ring.setWidth(3 if self._busy else (2 if self._hovered else 1))
        painter.setPen(ring)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(1, 1, size - 2, size - 2)

    def _paint_panel(self, painter: QPainter):
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 16, 16)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(*theme.PANEL_BG))
        painter.drawPath(path)

        pen = QPen(QColor(theme.PANEL_BORDER))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
