#!/usr/bin/env python3
"""
build_assets.py — Generate everything for the "Like It's 1999" TITANNET website.

Creates:
  1. All retro GIF images referenced by the HTML
  2. ISO 9660 CD image with all website files
  3. .gz compressed archive
  4. .bin/.cue CD image pair
"""

import os
import io
import gzip
import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent
ASSETS_DIR = PROJECT_DIR / "assets"
ISO_PATH = PROJECT_DIR / "titannet.iso"
GZ_PATH = PROJECT_DIR / "titannet.tar.gz"
BIN_PATH = PROJECT_DIR / "titannet.bin"
CUE_PATH = PROJECT_DIR / "titannet.cue"
BIN_ISO_PATH = PROJECT_DIR / "titannet_bin.iso"  # intermediate for .bin creation

# All files that go on the CD
WEBSITE_FILES = [
    "index.html",
    "guestbook.html",
    "assets/titannet_banner.gif",
    "assets/bg_stars.gif",
    "assets/button_home.gif",
    "assets/button_guestbook.gif",
    "assets/counter.gif",
    "assets/under_construction.gif",
    "assets/guestbook_banner.gif",
]

# ─── Font Setup ───────────────────────────────────────────────────────────────
def get_font(size):
    """Try to get a bold retro-looking font, fall back to default."""
    font_paths = [
        # Common Windows fonts that look retro
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/timesbd.ttf",
        "C:/Windows/Fonts/verdanab.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ─── Image Generators ─────────────────────────────────────────────────────────

def make_titannet_banner():
    """Main TITANNET banner — 600x100, fiery text on black."""
    img = Image.new("RGB", (600, 100), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Gradient background strip
    for y in range(100):
        r = max(0, min(255, int(80 + (y / 100) * 60)))
        for x in range(600):
            if (x + y) % 3 == 0 or (x - y) % 3 == 0:
                pass  # subtle scanline effect

    # Draw a 3D border
    for bx in range(5):
        color = (180 - bx * 20, 0, 0) if bx < 3 else (60, 0, 0)
        draw.rectangle([bx, bx, 599 - bx, 99 - bx], outline=color)

    # Decorative top and bottom bars
    draw.rectangle([5, 5, 594, 18], fill=(180, 0, 0))
    draw.rectangle([5, 82, 594, 95], fill=(180, 0, 0))

    # "TITANNET" text with bevel effect
    font_big = get_font(52)
    text = "TITANNET"
    # Shadow / bevel layers
    for offset, color in [(3, (80, 0, 0)), (2, (200, 50, 0)), (1, (255, 100, 0)), (0, (255, 200, 0))]:
        bbox = draw.textbbox((0, 0), text, font=font_big)
        tw = bbox[2] - bbox[0]
        x = (600 - tw) // 2 + offset
        y = 42 + offset
        draw.text((x, y), text, fill=color, font=font_big)

    # Subtitle
    font_small = get_font(10)
    draw.text((300, 25), "~ Attack on Titan Fan Site ~", fill=(200, 100, 100), font=font_small, anchor="mt")

    # "EST. 2026" in bottom right
    draw.text((580, 88), "EST. 2026", fill=(150, 50, 50), font=font_small, anchor="rb")

    return img


def make_bg_stars():
    """Star field background — 200x200 tiling pattern."""
    img = Image.new("RGB", (200, 200), (0, 0, 8))
    draw = ImageDraw.Draw(img)
    import random
    random.seed(42)
    for _ in range(150):
        x = random.randint(0, 199)
        y = random.randint(0, 199)
        brightness = random.randint(80, 255)
        size = random.choice([1, 1, 1, 2])
        draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, int(brightness * 0.8)))
    return img


def make_button(label, filename):
    """88x31 style navigation button with retro feel."""
    img = Image.new("RGB", (140, 40), (20, 0, 0))
    draw = ImageDraw.Draw(img)

    # Beveled border
    for bx in range(3):
        color = (200 - bx * 40, 40 - bx * 10, 40 - bx * 10) if bx < 2 else (60, 0, 0)
        draw.rectangle([bx, bx, 139 - bx, 39 - bx], outline=color)

    # Fire gradient background
    for y in range(6, 34):
        r = min(255, 120 + int((y / 28) * 80))
        g = min(255, max(0, int((y / 28) * 60 - 30)))
        draw.line([(6, y), (133, y)], fill=(r, g, 0))

    # Text with bevel
    font = get_font(14)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    x = (140 - tw) // 2
    draw.text((x + 1, 11 + 1), label, fill=(80, 20, 0), font=font)
    draw.text((x, 11), label, fill=(255, 220, 100), font=font)

    # Filename label on the button
    font_small = get_font(7)
    draw.text((3, 34), filename, fill=(150, 100, 100), font=font_small)
    return img


def make_counter():
    """88x31 visitor counter badge."""
    img = Image.new("RGB", (88, 31), (10, 10, 10))
    draw = ImageDraw.Draw(img)

    # Chrome/silver border
    for bx in range(2):
        draw.rectangle([bx, bx, 87 - bx, 30 - bx], outline=(120, 120, 120))

    # Dark blue inner area
    draw.rectangle([2, 2, 85, 29], fill=(0, 0, 40))

    # "VISITORS" label
    font = get_font(7)
    draw.text((44, 3), "VISITORS", fill=(200, 200, 200), font=font, anchor="mt")

    # The number in classic 7-segment style
    font_num = get_font(14)
    num_text = "00001999"
    bbox = draw.textbbox((0, 0), num_text, font=font_num)
    tw = bbox[2] - bbox[0]
    x = (88 - tw) // 2
    # Green glowing numbers
    for ox, oy in [(1, 1), (-1, -1), (0, 1), (1, 0)]:
        draw.text((x + ox, 12 + oy), num_text, fill=(0, 60, 0), font=font_num)
    draw.text((x, 12), num_text, fill=(0, 255, 0), font=font_num)

    # Small decoration
    draw.rectangle([3, 3, 12, 28], fill=(40, 0, 0))
    draw.rectangle([76, 3, 85, 28], fill=(40, 0, 0))
    return img


def make_under_construction():
    """Under construction banner — 400x40, animated-style (static frame)."""
    img = Image.new("RGB", (400, 40), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Yellow/black warning stripe border
    for x in range(400):
        stripe = (x // 8) % 2 == 0
        if x < 2 or x >= 398:
            continue
        color = (200, 200, 0) if stripe else (0, 0, 0)
        if x < 5 or x >= 395 or (x >= 2 and (x // 8) % 2 == 0):
            draw.line([(x, 0), (x, 5)], fill=color)
            draw.line([(x, 35), (x, 39)], fill=color)

    # Main text
    font = get_font(16)
    text = "*** UNDER CONSTRUCTION ***"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (400 - tw) // 2
    # Glow effect
    for ox, oy in [(2, 2), (-2, -2), (0, 2), (2, 0)]:
        draw.text((x + ox, 10 + oy), text, fill=(150, 50, 0), font=font)
    draw.text((x, 10), text, fill=(255, 200, 0), font=font)

    # Subtitle
    font_small = get_font(8)
    draw.text((200, 30), "Check back soon for updates!", fill=(200, 100, 100), font=font_small, anchor="mt")
    return img


def make_guestbook_banner():
    """Guestbook banner — 500x80."""
    img = Image.new("RGB", (500, 80), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(80):
        r = int(40 + (y / 80) * 100)
        draw.line([(0, y), (499, y)], fill=(r, 0, 0))

    # Border
    for bx in range(3):
        draw.rectangle([bx, bx, 499 - bx, 79 - bx], outline=(200 - bx * 50, 60, 60))

    # "GUESTBOOK" text with bevel
    font = get_font(36)
    text = "GUESTBOOK"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (500 - tw) // 2
    for offset, color in [(2, (80, 0, 0)), (1, (200, 80, 0)), (0, (255, 220, 50))]:
        draw.text((x + offset, 30 + offset), text, fill=color, font=font)

    # Underline decoration
    font_small = get_font(8)
    draw.text((250, 68), "=======================", fill=(200, 100, 100), font=font_small, anchor="mt")
    return img


def create_all_images():
    """Generate all GIF images and save to assets directory."""
    ASSETS_DIR.mkdir(exist_ok=True)

    print("Generating TITANNET banner...")
    img = make_titannet_banner()
    img.save(ASSETS_DIR / "titannet_banner.gif", format="GIF")

    print("Generating star field background...")
    img = make_bg_stars()
    img.save(ASSETS_DIR / "bg_stars.gif", format="GIF")

    print("Generating navigation buttons...")
    img = make_button("HOME", "button_home.gif")
    img.save(ASSETS_DIR / "button_home.gif", format="GIF")
    img = make_button("GUESTBOOK", "button_guestbook.gif")
    img.save(ASSETS_DIR / "button_guestbook.gif", format="GIF")

    print("Generating visitor counter...")
    img = make_counter()
    img.save(ASSETS_DIR / "counter.gif", format="GIF")

    print("Generating under construction sign...")
    img = make_under_construction()
    img.save(ASSETS_DIR / "under_construction.gif", format="GIF")

    print("Generating guestbook banner...")
    img = make_guestbook_banner()
    img.save(ASSETS_DIR / "guestbook_banner.gif", format="GIF")

    print(f"All images saved to {ASSETS_DIR}/")


# ─── ISO Creation ─────────────────────────────────────────────────────────────
def create_iso():
    """Create ISO 9660 CD image with all website files."""
    try:
        import pycdlib
    except ImportError:
        print("ERROR: pycdlib not installed. Run: pip install pycdlib")
        return False

    iso = pycdlib.PyCdlib()
    iso.new(vol_ident="TITANNET", joliet=3)

    # Use Joliet extensions to preserve original long filenames
    # ISO 9660 Level 1 gets 8.3 names; Joliet gets the original names
    file_map = [
        (PROJECT_DIR / "index.html",           "/INDEX.HTM",  "/INDEX.HTM"),
        (PROJECT_DIR / "guestbook.html",       "/GUESTBOK.HTM", "/GUESTBOOK.HTML"),
        (ASSETS_DIR / "titannet_banner.gif",   "/BANNER.GIF", "/TITANNET_BANNER.GIF"),
        (ASSETS_DIR / "bg_stars.gif",          "/BGSTARS.GIF", "/BG_STARS.GIF"),
        (ASSETS_DIR / "button_home.gif",       "/BTNHOME.GIF", "/BUTTON_HOME.GIF"),
        (ASSETS_DIR / "button_guestbook.gif",  "/BTNGUEST.GIF", "/BUTTON_GUESTBOOK.GIF"),
        (ASSETS_DIR / "counter.gif",           "/COUNTER.GIF", "/COUNTER.GIF"),
        (ASSETS_DIR / "under_construction.gif","/UNDERCON.GIF", "/UNDER_CONSTRUCTION.GIF"),
        (ASSETS_DIR / "guestbook_banner.gif",  "/GUESTBNR.GIF", "/GUESTBOOK_BANNER.GIF"),
    ]

    iso.write(str(ISO_PATH))
    iso.close()
    print(f"ISO created: {ISO_PATH} ({ISO_PATH.stat().st_size:,} bytes)")
    return True


# ─── .gz Archive Creation ─────────────────────────────────────────────────────
def create_gz_archive():
    """Create a gzip-compressed tar archive of the website files."""
    import tarfile

    with tarfile.open(str(GZ_PATH), "w:gz") as tar:
        for rel_path in WEBSITE_FILES:
            local_path = PROJECT_DIR / rel_path
            if local_path.exists():
                print(f"  Archiving: {rel_path}")
                tar.add(str(local_path), arcname=rel_path)
            else:
                print(f"  WARNING: {local_path} not found, skipping")

    print(f"GZ archive created: {GZ_PATH} ({GZ_PATH.stat().st_size:,} bytes)")


# ─── .bin/.cue CD Image Creation ──────────────────────────────────────────────
def create_bin_cue():
    """Create a .bin/.cue CD image pair from the ISO."""
    if not ISO_PATH.exists():
        print("ERROR: ISO file not found. Run ISO creation first.")
        return False

    # Read the ISO
    with open(ISO_PATH, "rb") as f:
        iso_data = f.read()

    iso_size = len(iso_data)

    # For a data CD, the .bin file contains 2352-byte sectors.
    # The ISO (2048 bytes/sector) sits inside each sector with 16 bytes of
    # sync + 4 bytes of header + 2048 bytes data + 280 bytes of ECC/EDC.
    # To make it simple and compatible with most emulators, we create a
    # "raw" .bin by padding each 2048-byte ISO sector to 2352 bytes.

    sector_count = iso_size // 2048
    if iso_size % 2048 != 0:
        sector_count += 1

    print(f"  Creating .bin with {sector_count} sectors...")

    with open(BIN_PATH, "wb") as f:
        for i in range(sector_count):
            start = i * 2048
            chunk = iso_data[start:start + 2048]
            # Standard Mode 1 CD-ROM sector: 2352 bytes
            #   12 sync + 3 addr + 1 mode + 2048 data + 4 edc + 8 reserved + 276 ecc = 2352
            m, s, fr = (i // 4500) % 100, (i % 4500) // 75, i % 75
            sector = b"\x00" * 12           # sync pattern (all zeros is fine)
            sector += struct.pack("BBB", m, s, fr)  # address (min, sec, frame)
            sector += b"\x01"               # Mode 1
            sector += chunk                  # 2048 bytes data
            # Pad the rest to 2352 exactly
            sector += b"\x00" * (2352 - len(sector))
            assert len(sector) == 2352, f"Sector {i} has wrong size: {len(sector)}"
            f.write(sector)

    print(f"  .bin created: {BIN_PATH} ({BIN_PATH.stat().st_size:,} bytes)")

    # Create .cue file
    bin_stem = BIN_PATH.name
    with open(CUE_PATH, "w") as f:
        f.write(f'FILE "{bin_stem}" BINARY\n')
        f.write("  TRACK 01 MODE1/2352\n")
        f.write("    INDEX 01 00:00:00\n")

    print(f"  .cue created: {CUE_PATH}")
    return True


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  LIKE IT'S 1999 — Asset Builder")
    print("  Building assets for TITANNET website")
    print("=" * 60)
    print()

    # Step 1: Generate images
    print("[1/4] Generating retro GIF images...")
    print("-" * 40)
    create_all_images()
    print()

    # Step 2: Create ISO
    print("[2/4] Creating ISO 9660 CD image...")
    print("-" * 40)
    create_iso()
    print()

    # Step 3: Create .gz archive
    print("[3/4] Creating .gz compressed archive...")
    print("-" * 40)
    create_gz_archive()
    print()

    # Step 4: Create .bin/.cue
    print("[4/4] Creating .bin/.cue CD image pair...")
    print("-" * 40)
    create_bin_cue()
    print()

    print("=" * 60)
    print("  BUILD COMPLETE!")
    print("=" * 60)
    print()
    print("Files created:")
    for f in sorted(PROJECT_DIR.glob("titannet.*")):
        print(f"  {f.name} ({f.stat().st_size:>8,} bytes)")
    for f in sorted(ASSETS_DIR.glob("*")):
        print(f"  assets/{f.name} ({f.stat().st_size:>8,} bytes)")
    print()
    print("To import into Windows 98 (99.hackclub.com):")
    print("  1. Mount titannet.iso as a CD-ROM in the emulator")
    print("  2. OR use 'Send files to emulator' with individual files")
    print("  3. OR use titannet.bin as a raw CD image")
    print("  4. OR extract titannet.tar.gz on your host machine")


if __name__ == "__main__":
    main()
