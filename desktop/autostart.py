"""Autostart via the XDG autostart spec: a .desktop file in
~/.config/autostart/ that KDE/GNOME/most Linux desktop environments
launch automatically at login. No systemd unit needed for a per-user
GUI app -- this is the standard mechanism apps like Vesktop/Discord use
on this same machine (see ~/.config/autostart/dev.vencord.Vesktop.desktop).
"""

from pathlib import Path

from config import settings

AUTOSTART_DIR = Path.home() / ".config" / "autostart"
AUTOSTART_FILE = AUTOSTART_DIR / "characterengine.desktop"

PYTHON_BIN = settings.PROJECT_ROOT / "venv" / "bin" / "python"
MAIN_SCRIPT = settings.PROJECT_ROOT / "main.py"
ICON_PATH = settings.PROJECT_ROOT / "icon.png"


def is_enabled() -> bool:
    return AUTOSTART_FILE.exists()


def enable(delay_seconds: int = 0) -> None:
    """Write the autostart entry. delay_seconds waits before launching,
    in case the desktop environment/network isn't fully up yet at login
    (spec's "optional delay after system startup")."""
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)

    if delay_seconds > 0:
        exec_line = f'sh -c "sleep {delay_seconds}; \\"{PYTHON_BIN}\\" \\"{MAIN_SCRIPT}\\" desktop"'
    else:
        exec_line = f'"{PYTHON_BIN}" "{MAIN_SCRIPT}" desktop'

    contents = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=CharacterEngine\n"
        "Comment=Local AI companion framework\n"
        f"Exec={exec_line}\n"
        f"Icon={ICON_PATH}\n"
        "Terminal=false\n"
        "X-GNOME-Autostart-enabled=true\n"
    )
    AUTOSTART_FILE.write_text(contents, encoding="utf-8")


def disable() -> None:
    if AUTOSTART_FILE.exists():
        AUTOSTART_FILE.unlink()


def toggle(delay_seconds: int = 0) -> bool:
    """Flip autostart on/off. Returns the new state."""
    if is_enabled():
        disable()
        return False
    enable(delay_seconds)
    return True
