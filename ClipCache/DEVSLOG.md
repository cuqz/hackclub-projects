# Devlog — ClipCache

## Session 1: Foundation

**Date:** 2026-07-07
**Time tracked:** ~2.5 hours

### What I built

ClipCache is a desktop clipboard manager for Windows that runs in the system tray. It solves the eternal problem: Windows clipboard holds one thing, you copy something else, and the first thing is gone forever.

### Core features implemented

- **Clipboard monitoring** — polls the system clipboard every 400ms, saves text changes to SQLite
- **Searchable history** — live search as you type through up to 500 recent items
- **Pin system** — pin important snippets so they stay at the top across sessions
- **System tray integration** — runs silently, accessible via tray icon
- **Global hotkey (Ctrl+Shift+V)** — pop the window from anywhere in one keystroke
- **One-click recopy** — click any item to copy it back to clipboard, window auto-hides
- **Sensitive content filter** — automatically skips API keys, private keys, and tokens
- **Dark mode UI** — built with customtkinter, clean bento-style cards
- **Clear history with confirmation** — one button to wipe unpinned items
- **500-item auto-trim** — oldest unpinned items get pruned automatically

### Technical decisions

- **Python + customtkinter** over Electron/Tauri — lighter weight, no node_modules hell, runs on any Windows machine with Python
- **SQLite with WAL mode** — concurrent read/write without locks, no server process
- **Time tracking** — used WakaTime for session logging

### Challenges

- The `keyboard` library for global hotkeys needs admin rights on some Windows configs. Need to add a fallback or clearer error message for users who can't get the hotkey working.
- Thread safety in the clipboard monitor — had a race where `copy_to_clipboard` could spawn duplicate polling threads. Fixed with a thread join.
- customtkinter canvas scrolling needed careful binding to get mousewheel + keyboard nav working simultaneously.

## Session 2: Keyboard Nav, Export/Import, Status Bar

**Date:** 2026-07-07 (later same day)
**Time tracked:** ~25 mins

### What I added

Kicked off the Hack Club session properly, then dove into real features:

**Keyboard navigation** — you can now use Up/Down arrows to move through the clipboard list, Enter to copy the selected item. Also bound Ctrl-P / Ctrl-N for the vim crowd (lol). The highlight follows your selection with a red accent border. Tried to get auto-scroll working but it's glitchy -- scrolls to roughly the right spot but not perfectly. TODO: come back and fix this.

**Status bar** — tiny bar at the bottom showing "3 / 47 | Enter to copy" type info. Also shows the version number on the right because why not.

**Export/Import** — you can now export your pinned items as a JSON file, and import them back on another machine. Uses Windows file dialogs natively. This was trickier than I thought because of duplicate detection -- ended up just skipping items where content matches an existing pinned item.

**Sensitive content filter** — removed an overly aggressive base64 regex that was flagging everything. Kept the private key / GitHub token / OpenAI key patterns which are more targeted.

### Bugs fixed this session

- Pinned cards losing their color on mouse hover (forgot to track pinned state per card)
- Thread race in clipboard monitor copy-back (old polling thread colliding with new one)
- Removed dead import and dead code _export_history that was defined but never called

### Random thoughts

- customtkinter is actually pretty good for quick desktop apps. Not as polished as native WinUI but way faster to build with.
- The keyboard library for hotkeys is janky on Windows -- needs admin sometimes. Might switch to a ctypes-based approach for v2.
- I keep wanting to add features but I should probably ship this first. MVP is solid.

### What's next

- Build a standalone .exe with PyInstaller
- Auto-start with Windows option (registry key)
- Image clipboard detection (at least show "📷 image copied" placeholder)
- Maybe a dark/light mode toggle
