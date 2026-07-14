# ClipCache

Clipboard manager for Windows. Lives in the system tray. Saves everything you copy so you don't lose it.

## What it does

Windows clipboard only holds one thing at a time. ClipCache watches what you copy and keeps a history of the last 500 items. Press Ctrl+Shift+V to open the list, search through it, click anything to copy it back.

## Features

- Saves every text you copy automatically
- Search through your history
- Pin stuff you use a lot so it stays at the top
- Ctrl+Shift+V opens the window from anywhere
- Click anything to copy it back
- Dark theme, runs in the background
- Everything saved locally, nothing uploaded anywhere

## How to run

```
pip install -r requirements.txt
python main.py
```

To make it a standalone exe:
```
pip install pyinstaller
pyinstaller --onefile --windowed --icon assets/icon.ico main.py
```

## Why

Got tired of losing copied stuff. Ctrl+C something, Ctrl+C something else, first thing's gone. This fixes that.
