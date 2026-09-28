"""Single source of truth for the desktop UI's palette (spec §15/§20:
config over hard-coding). Swap ACCENT/ACCENT_DIM to switch the whole app
between the dark-red and amber accent options."""

PANEL_BG = (23, 24, 28, 235)  # charcoal, translucent
PANEL_BORDER = "#3a3b42"

TEXT_PRIMARY = "#e8e8ec"
TEXT_SECONDARY = "#9a9ba3"
TEXT_MUTED = "#65666e"

ACCENT = "#b3413f"      # dark red (alternative: "#c98a2c" amber)
ACCENT_DIM = "#7a2c2b"

MOOD_COLORS = {
    "neutral": "#8a8b92",
    "happy": "#c98a2c",
    "amused": "#c98a2c",
    "curious": "#4f8fc0",
    "excited": "#c98a2c",
    "annoyed": "#b3413f",
    "angry": "#b3413f",
    "sad": "#4f6fc0",
    "worried": "#4f6fc0",
    "disappointed": "#7a2c2b",
    "embarrassed": "#c06f9a",
    "suspicious": "#8a8b92",
    "affectionate": "#c06f9a",
    "playful": "#c98a2c",
    "tired": "#65666e",
    "bored": "#65666e",
    "nostalgic": "#8a7fc0",
}


def mood_color(mood: str) -> str:
    return MOOD_COLORS.get((mood or "").lower(), TEXT_SECONDARY)


PANEL_QSS = f"""
QWidget#chatPanel {{
    background: transparent;
}}
QTextEdit#chatLog {{
    background: transparent;
    border: none;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    padding: 4px;
}}
QLineEdit#inputBox {{
    background: #1f2025;
    border: 1px solid {PANEL_BORDER};
    border-radius: 10px;
    color: {TEXT_PRIMARY};
    padding: 8px 10px;
    font-size: 13px;
}}
QLineEdit#inputBox:focus {{
    border: 1px solid {ACCENT};
}}
QPushButton#sendButton {{
    background: {ACCENT};
    border: none;
    border-radius: 10px;
    color: {TEXT_PRIMARY};
    font-weight: 600;
    padding: 8px 14px;
}}
QPushButton#sendButton:hover {{
    background: {ACCENT_DIM};
}}
QPushButton#sendButton:disabled {{
    background: #3a3b42;
    color: {TEXT_MUTED};
}}
QPushButton#headerButton {{
    background: transparent;
    border: none;
    color: {TEXT_SECONDARY};
    font-size: 15px;
}}
QPushButton#headerButton:hover {{
    color: {TEXT_PRIMARY};
}}
QLabel#nameLabel {{
    color: {TEXT_PRIMARY};
    font-size: 14px;
    font-weight: 600;
}}
QLabel#statusLabel {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {PANEL_BORDER};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""
