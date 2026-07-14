#!/usr/bin/env python3
"""
ClipCache — Desktop Clipboard Manager

A system-tray clipboard history app for Windows.
Saves everything you copy, searchable, pinnable, always a hotkey away.
"""

import sys
from app import database
from app.clipboard import ClipboardMonitor
from app.ui import ClipCacheUI
from app.tray import TrayManager
from app.hotkey import HotkeyManager
from app.version import VERSION, BUILD


def show_version():
    print(f"ClipCache v{VERSION}")
    print(f"Build: {BUILD}")
    print("A desktop clipboard manager for Windows.")
    print("https://github.com/wezamwiwa/clipcache")


def main():
    # Initialize DB
    database.init_db()

    # Start clipboard monitor
    monitor = ClipboardMonitor()

    # Build UI
    ui = ClipCacheUI(monitor)

    # Connect monitor to UI
    monitor.start(on_change=lambda content, item_id: ui.refresh())

    # System tray
    tray = TrayManager(
        show_callback=lambda: ui.window.after(0, ui.show),
        quit_callback=lambda: ui.window.after(0, ui.close),
    )
    tray.start()

    # Global hotkey: Ctrl+Shift+V
    hotkey = HotkeyManager(callback=lambda: ui.window.after(0, ui.show))
    hotkey.start()

    print(f"[ClipCache] v{VERSION} running in system tray. Press Ctrl+Shift+V to open.")
    print("[ClipCache] Pin items with the pin button, click to copy, search to find.")

    try:
        ui.run()
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()
        hotkey.stop()
        tray.stop()


if __name__ == "__main__":
    if "--version" in sys.argv or "-v" in sys.argv:
        show_version()
        sys.exit(0)
    main()
