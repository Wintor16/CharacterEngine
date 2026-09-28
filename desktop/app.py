"""Desktop presence entry point: a persistent, always-on-top floating
avatar backed by the same CharacterEngine as the CLI and web UI.

QT_QPA_PLATFORM=xcb is forced (via XWayland) before QApplication exists,
because native Wayland compositors generally refuse to let a client
position or drag a top-level window -- both of which this floating
avatar depends on. XWayland gives the traditional X11 semantics this
kind of widget needs, on any desktop environment.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from brain.proactive import ProactiveEngine
from character.manager import CharacterManager
from config import settings
from core.engine import CharacterEngine
from desktop import autostart
from desktop.engine_worker import ReplyWorker
from desktop.floating_window import FloatingWindow, ICON_PATH
from events.bus import Event, EventBus
from scheduler.reminders import ReminderScheduler


def main(reset_state: bool = False, character_name_override: str = None):
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    manager = CharacterManager()
    character = manager.load(settings.DEFAULT_CHARACTER)
    if character_name_override:
        # Isolates every file this run touches (state, memory, reminders)
        # under a different name, so the desktop app can be tested
        # without ever reading or writing the real character's data.
        character.identity["name"] = character_name_override
    engine = CharacterEngine(character)

    if reset_state:
        engine.reset_everything()
        print("[Reset - starting with a blank slate: no memories, default mood/relationship]")

    display_name = character.identity.get("name", "Kurumi")

    window = FloatingWindow(engine, display_name)
    window.show()

    # ---------------------------------
    # Proactive behavior (spec Phase 8)
    # ---------------------------------
    # EVENT -> RELEVANCE -> IMPORTANCE -> STATE -> DECISION -> ACTION.
    # The "event" here is simply idle time crossing a threshold -- there's
    # no OS-level event bus yet (file/app watchers, a separate phase).
    # Most checks end in silence; see brain/proactive.py for the gating.
    proactive_engine = ProactiveEngine()
    ui_state = {"proactive_enabled": settings.PROACTIVE_ENABLED, "proactive_worker": None}

    def on_proactive_ready(response):
        if response.success and response.text.strip():
            window.show_notification(response.text)
        ui_state["proactive_worker"] = None

    def check_proactive():
        if not ui_state["proactive_enabled"] or ui_state["proactive_worker"] is not None:
            return
        decision = proactive_engine.evaluate(engine.brain.state, engine.last_interaction_at)
        if not decision.should_speak:
            return
        # Genuinely generated through the real engine from the occasion
        # cue, not a canned line -- see brain/proactive.py. Runs in the
        # background like any other reply so the UI doesn't freeze.
        worker = ReplyWorker(engine, decision.occasion, is_proactive=True)
        worker.succeeded.connect(on_proactive_ready)
        worker.failed.connect(lambda err: ui_state.__setitem__("proactive_worker", None))
        ui_state["proactive_worker"] = worker
        worker.start()

    proactive_timer = QTimer()
    proactive_timer.timeout.connect(check_proactive)
    proactive_timer.start(settings.PROACTIVE_CHECK_INTERVAL_MINUTES * 60 * 1000)

    # ---------------------------------
    # Scheduled reminders (Step 7: events + scheduler)
    # ---------------------------------
    # A fired reminder is functionally a proactive notification, so it
    # reuses the exact same worker slot/callback as check_proactive()
    # above -- see ui_state["proactive_worker"] and on_proactive_ready.
    reminder_scheduler = ReminderScheduler(character.identity["name"])
    event_bus = EventBus(min_gap_minutes=1.0)

    def check_reminders():
        if ui_state["proactive_worker"] is not None:
            return
        for reminder in reminder_scheduler.pop_due():
            event = Event(type="reminder_due", payload={"message": reminder.message}, importance=1.0)
            if not event_bus.should_act(event):
                continue
            event_bus.mark_handled(event)
            occasion = f'*Something you were asked to remember resurfaces now: "{reminder.message}"*'
            # is_proactive=True is required here -- it's what stops a
            # fired reminder from resetting engine.last_interaction_at,
            # which would corrupt the idle-time clock ProactiveEngine
            # depends on above.
            worker = ReplyWorker(engine, occasion, is_proactive=True)
            worker.succeeded.connect(on_proactive_ready)
            worker.failed.connect(lambda err: ui_state.__setitem__("proactive_worker", None))
            ui_state["proactive_worker"] = worker
            worker.start()
            break  # one at a time; any other due reminders are picked up next tick

    reminder_timer = QTimer()
    reminder_timer.timeout.connect(check_reminders)
    reminder_timer.start(settings.SCHEDULER_CHECK_INTERVAL_SECONDS * 1000)

    icon = QIcon(str(ICON_PATH)) if ICON_PATH.exists() else app.windowIcon()
    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip(f"{display_name} - Kurumi AI")

    menu = QMenu()
    show_action = menu.addAction("Show Kurumi")
    show_action.triggered.connect(lambda: (window.show(), window.show_compact()))
    hide_action = menu.addAction("Hide")
    hide_action.triggered.connect(window.show_avatar)
    menu.addSeparator()
    proactive_action = menu.addAction("Proactive messages")
    proactive_action.setCheckable(True)
    proactive_action.setChecked(ui_state["proactive_enabled"])
    proactive_action.toggled.connect(lambda checked: ui_state.__setitem__("proactive_enabled", checked))
    # Manual trigger, useful for testing without waiting out the real
    # idle/cooldown gates in brain/proactive.py. Still goes through real
    # generation, same as the automatic path -- never a fixed string.
    def send_test_notification():
        if ui_state["proactive_worker"] is not None:
            return
        occasion = proactive_engine._pick_occasion(engine.brain.state, idle_minutes=999)
        worker = ReplyWorker(engine, occasion, is_proactive=True)
        worker.succeeded.connect(on_proactive_ready)
        worker.failed.connect(lambda err: ui_state.__setitem__("proactive_worker", None))
        ui_state["proactive_worker"] = worker
        worker.start()

    notify_action = menu.addAction("Send test notification")
    notify_action.triggered.connect(send_test_notification)

    # Test-only affordance to exercise the reminder pipeline end to end.
    # Real reminder-creation UX (chat command vs. dialog vs. a future
    # tool call) is a deliberately separate, not-yet-made decision.
    def add_test_reminder():
        reminder_scheduler.add("Testing the reminder pipeline.", datetime.now() + timedelta(minutes=1))

    test_reminder_action = menu.addAction("Set test reminder (1 min)")
    test_reminder_action.triggered.connect(add_test_reminder)

    debug_action = menu.addAction("Debug mode")
    debug_action.setCheckable(True)
    debug_action.setChecked(False)
    debug_action.setToolTip("Shows model/timing/decision info in the expanded (⤢) view")
    debug_action.toggled.connect(window.chat_panel.set_debug_enabled)
    menu.addSeparator()
    autostart_action = menu.addAction("Start automatically at login")
    autostart_action.setCheckable(True)
    autostart_action.setChecked(autostart.is_enabled())
    autostart_action.toggled.connect(
        lambda checked: autostart.enable(settings.AUTOSTART_DELAY_SECONDS) if checked else autostart.disable()
    )
    menu.addSeparator()

    def do_reset():
        answer = QMessageBox.question(
            None,
            "Reset Kurumi",
            "This permanently erases her memories, relationship, mood, "
            "and conversation history, and starts completely fresh. "
            "This cannot be undone.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        engine.reset_everything()
        window.chat_panel.chat_log.clear()
        window.chat_panel.status_dot.setStyleSheet("color: #8a8b92; font-size: 12px;")
        window.chat_panel.status_label.setText("neutral")
        if window.chat_panel._expanded:
            window.chat_panel.stats_panel.refresh(engine.brain.state)
        window.chat_panel.greet("*The clock resets. A blank page.* ...Who are you again?")

    reset_action = menu.addAction("Reset Kurumi (forget everything)")
    reset_action.triggered.connect(do_reset)

    menu.addSeparator()

    def restart_app():
        # A plain process relaunch, not a reset -- state/memory are all
        # file-backed and reload from disk on the next startup exactly as
        # they are now, untouched. Useful for picking up a config change
        # or just recovering from a stuck session. sys.orig_argv (not
        # sys.argv) preserves the original interpreter flags too (e.g.
        # -u), not just the script's own arguments.
        tray.hide()
        os.execv(sys.orig_argv[0], sys.orig_argv)

    restart_action = menu.addAction("Restart Kurumi AI")
    restart_action.setToolTip("Relaunches the app. Memory and relationship are untouched.")
    restart_action.triggered.connect(restart_app)

    menu.addSeparator()
    quit_action = menu.addAction("Quit")
    quit_action.triggered.connect(app.quit)
    tray.setContextMenu(menu)

    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            window.show()
            window.show_compact()

    tray.activated.connect(on_tray_activated)
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
