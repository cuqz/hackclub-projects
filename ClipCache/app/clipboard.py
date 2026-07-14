import re
import sys
import pyperclip
import threading
import time
from . import database


POLL_INTERVAL = 0.4  # seconds

# Skip items that look like sensitive credentials
_SENSITIVE_PATTERNS = [
    re.compile(r'^-----BEGIN (RSA |EC )?PRIVATE KEY-----', re.IGNORECASE),
    re.compile(r'^(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}$'),  # GitHub tokens
    re.compile(r'^sk-[A-Za-z0-9]{32,}$'),  # OpenAI-style keys
]


class ClipboardMonitor:
    def __init__(self):
        self._last_content: str = ""
        self._running = False
        self._thread: threading.Thread | None = None
        self._on_change = None
        try:
            self._last_content = pyperclip.paste()
        except Exception:
            self._last_content = ""

    @property
    def last_content(self) -> str:
        return self._last_content

    def start(self, on_change=None):
        self._on_change = on_change
        self._running = True
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _is_sensitive(self, text: str) -> bool:
        """Check if text looks like sensitive credentials."""
        return any(p.search(text) for p in _SENSITIVE_PATTERNS)

    def _poll(self):
        while self._running:
            try:
                current = pyperclip.paste()
                if current and current != self._last_content:
                    self._last_content = current
                    if self._is_sensitive(current):
                        continue  # Skip sensitive content
                    item_id = database.add_item(current)
                    if item_id and self._on_change:
                        self._on_change(current, item_id)
            except Exception as e:
                print(f"[ClipCache] Clipboard error: {e}", file=sys.stderr)
            time.sleep(POLL_INTERVAL)

    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard (temporarily pause monitoring)."""
        was_running = self._running
        if was_running:
            self.stop()
        try:
            pyperclip.copy(text)
            self._last_content = text
        finally:
            if was_running:
                self.start(self._on_change)
