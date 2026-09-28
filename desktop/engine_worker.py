"""Runs CharacterEngine.reply() off the GUI thread. LLM generation is a
blocking call; without this the floating window would freeze on every
message."""

from PySide6.QtCore import QThread, Signal


class ReplyWorker(QThread):
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, engine, message: str, parent=None, is_proactive: bool = False):
        super().__init__(parent)
        self.engine = engine
        self.message = message
        self.is_proactive = is_proactive

    def run(self):
        try:
            response = self.engine.reply(self.message, is_proactive=self.is_proactive)
            if response.success:
                self.succeeded.emit(response)
            else:
                self.failed.emit(response.error or "Unknown error")
        except Exception as e:
            self.failed.emit(str(e))
