import threading
import keyboard


HOTKEY = "ctrl+shift+v"


class HotkeyManager:
    def __init__(self, callback):
        self._callback = callback
        self._running = False

    def start(self):
        self._running = True
        try:
            keyboard.add_hotkey(HOTKEY, self._on_hotkey, suppress=True)
        except Exception as e:
            print(f"[ClipCache] Failed to register hotkey {HOTKEY}: {e}")

    def stop(self):
        self._running = False
        try:
            keyboard.remove_hotkey(HOTKEY)
        except Exception:
            pass

    def _on_hotkey(self):
        if self._callback and self._running:
            self._callback()
