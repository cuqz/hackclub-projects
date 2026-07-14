import threading
import pystray
from PIL import Image, ImageDraw


def _create_icon_image() -> Image.Image:
    """Generate a simple clipboard icon."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Clipboard body
    draw.rectangle([14, 18, 50, 58], fill=(233, 69, 96), outline=(200, 50, 70), width=2)
    # Clipboard clip
    draw.rectangle([24, 10, 40, 20], fill=(233, 69, 96), outline=(200, 50, 70), width=2)
    # Checkmark
    draw.line([22, 38, 30, 48], fill=(255, 255, 255), width=3)
    draw.line([30, 48, 44, 30], fill=(255, 255, 255), width=3)

    return img


class TrayManager:
    def __init__(self, show_callback, quit_callback):
        self._show_callback = show_callback
        self._quit_callback = quit_callback
        self._icon = None
        self._thread = None

    def start(self):
        icon_image = _create_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show ClipCache", self._on_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )
        self._icon = pystray.Icon("clipcache", icon_image, "ClipCache", menu)
        # Run in daemon thread so it doesn't block shutdown
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def _on_show(self):
        if self._show_callback:
            self._show_callback()

    def _on_quit(self):
        if self._quit_callback:
            self._quit_callback()
        if self._icon:
            self._icon.stop()

    def stop(self):
        if self._icon:
            self._icon.stop()
