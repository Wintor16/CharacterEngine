import json
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional


class ShortMemory:
    """Recent conversation buffer sent to the LLM each turn.

    Backed by an append-only log (when log_path is given) so the actual
    conversation survives a restart -- previously this was pure
    in-memory, so every relaunch started with zero continuity beyond
    whatever fragments MemoryConsolidator happened to judge "important
    enough" for long-term memory. The full log is kept indefinitely (not
    just the last `limit` messages) even though only the tail is loaded
    back into the live buffer, since the LLM's own context window can't
    hold everything.
    """

    def __init__(self, limit: int = 8, log_path: Optional[Path] = None):
        self.limit = limit
        self.messages = deque(maxlen=limit)
        self.log_path = log_path

        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self._load_tail()

    def _load_tail(self):
        if not self.log_path.exists():
            return
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines[-self.limit:]:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                self.messages.append({"role": entry["role"], "content": entry["content"]})
        except Exception as e:
            print(f"[ShortMemory] Failed to load conversation log, starting fresh: {e}")

    def _append_log(self, role: str, content: str):
        if not self.log_path:
            return
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                }, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[ShortMemory] Failed to append to conversation log: {e}")

    def add(
        self,
        role: str,
        content: str
    ):
        self.messages.append({
            "role": role,
            "content": content
        })
        self._append_log(role, content)

    def all(self):
        return list(self.messages)

    def clear(self):
        """Wipe both the live buffer and the persisted log. Deliberately
        wipes both -- if only the live buffer were cleared, a restart
        would silently reload the old conversation from the log and
        undo the reset, which would be more confusing than clearing
        everything."""
        self.messages.clear()
        if self.log_path and self.log_path.exists():
            self.log_path.unlink()
