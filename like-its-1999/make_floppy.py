"""
make_floppy.py — 1.44MB FAT12 floppy disk image (.img)
with VFAT long filename support, for mounting in 99.hackclub.com
Windows 98 emulator (v86).

Files keep their original names (no 8.3 truncation) thanks to VFAT.
"""

import os
import struct
import math
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
ASSETS_DIR = PROJECT_DIR / "assets"
FLOPPY_PATH = PROJECT_DIR / "titannet.img"

# 1.44MB 3.5" HD floppy geometry
BYTES_PER_SECTOR = 512
SECTORS_PER_CLUSTER = 1
RESERVED_SECTORS = 1
NUM_FATS = 2
ROOT_ENTRIES = 224
TOTAL_SECTORS = 2880
MEDIA_DESCRIPTOR = 0xF0
SECTORS_PER_FAT = 9
SECTORS_PER_TRACK = 18
NUM_HEADS = 2
HIDDEN_SECTORS = 0

ROOT_DIR_SECTORS = (ROOT_ENTRIES * 32 + BYTES_PER_SECTOR - 1) // BYTES_PER_SECTOR
FIRST_DATA_SECTOR = RESERVED_SECTORS + (NUM_FATS * SECTORS_PER_FAT) + ROOT_DIR_SECTORS
TOTAL_DATA_SECTORS = TOTAL_SECTORS - FIRST_DATA_SECTOR
TOTAL_CLUSTERS = TOTAL_DATA_SECTORS // SECTORS_PER_CLUSTER
FAT_SIZE = SECTORS_PER_FAT * BYTES_PER_SECTOR


# ─── Boot Sector ──────────────────────────────────────────────────────────────

def make_bootsector():
    """Build a valid FAT12 BPB + boot sector for a 1.44MB floppy."""
    bpb = bytearray()
    bpb += b"\xeb\x3c\x90"            # jmp short + nop
    bpb += b"TITANNET"                # OEM name (8 bytes)
    bpb += struct.pack("<H", BYTES_PER_SECTOR)
    bpb += struct.pack("B", SECTORS_PER_CLUSTER)
    bpb += struct.pack("<H", RESERVED_SECTORS)
    bpb += struct.pack("B", NUM_FATS)
    bpb += struct.pack("<H", ROOT_ENTRIES)
    bpb += struct.pack("<H", TOTAL_SECTORS)
    bpb += struct.pack("B", MEDIA_DESCRIPTOR)
    bpb += struct.pack("<H", SECTORS_PER_FAT)
    bpb += struct.pack("<H", SECTORS_PER_TRACK)
    bpb += struct.pack("<H", NUM_HEADS)
    bpb += struct.pack("<I", HIDDEN_SECTORS)
    bpb += struct.pack("<I", 0)         # total sectors (large)
    bpb += struct.pack("B", 0x00)       # drive number
    bpb += struct.pack("B", 0x00)       # reserved
    bpb += struct.pack("B", 0x29)       # extended boot sig
    bpb += struct.pack("<I", 0x19990711)  # volume serial
    bpb += b"TITANNET   "              # volume label (11 bytes)
    bpb += b"FAT12   "                 # fs type (8 bytes)

    assert len(bpb) == 62, f"BPB: {len(bpb)} (expect 62)"
    return bytes(bpb) + b"\x00" * 448 + b"\x55\xAA"


# ─── 8.3 Short Filename ──────────────────────────────────────────────────────

def to_83(name):
    """Encode a filename to 8.3 uppercase DOS format (11 bytes)."""
    name = name.upper()
    if "." in name:
        base, ext = name.rsplit(".", 1)
        base = base[:8].ljust(8, " ")
        ext = ext[:3].ljust(3, " ")
    else:
        base = name[:8].ljust(8, " ")
        ext = "   "
    return base.encode("ascii") + ext.encode("ascii")


# ─── VFAT Long Filename Entries ──────────────────────────────────────────────

def vfat_csum(short_bytes):
    """VFAT checksum of an 8.3 filename."""
    c = 0
    for b in short_bytes:
        c = (((c & 1) << 7) | ((c >> 1) & 0x7F)) + b
        c &= 0xFF
    return c


def make_vfat(name, short_bytes):
    """
    Create VFAT long-filename directory entries.

    Each VFAT entry carries 13 UTF-16LE characters.
    Returns list of 32-byte entries (to be placed BEFORE the 8.3 entry).
    """
    # Filename encoded as UTF-16LE + null terminator + pad to 13-char boundary
    raw = name.encode("utf-16-le") + b"\x00\x00"
    raw += b"\xff\xff" * ((26 - len(raw) % 26) % 26 // 2)

    n_entries = max(1, (len(raw) + 25) // 26)
    csum = vfat_csum(short_bytes)
    entries = []

    for i in range(n_entries):
        ent = bytearray(32)
        seq = n_entries - i
        ent[0] = seq | (0x40 if i == 0 else 0x00)  # last marker
        ent[11] = 0x0F          # VFAT attribute
        ent[12] = 0             # type
        ent[13] = csum          # checksum

        chunk = raw[i * 26: (i + 1) * 26]
        if len(chunk) < 26:
            chunk += b"\xff\xff" * ((26 - len(chunk)) // 2)
        ent[1:11] = chunk[0:10]    # chars 0-4 (10 bytes)
        ent[14:26] = chunk[10:22]  # chars 5-10 (12 bytes)
        ent[28:32] = chunk[22:26]  # chars 11-12 (4 bytes)

        entries.append(bytes(ent))

    return entries


# ─── Root Directory ───────────────────────────────────────────────────────────

def build_root_dir(files):
    """
    Build root directory with VFAT long filename entries.

    files: list of (name, data, first_cluster)
    Returns bytes (always ROOT_ENTRIES * 32 = 7168 bytes).
    """
    buf = bytearray()
    for name, data, cluster in files:
        short = to_83(name)
        buf += b"".join(make_vfat(name, short))
        # 8.3 entry
        ent = bytearray(32)
        ent[0:11] = short
        ent[11] = 0x20                     # archive
        struct.pack_into("<H", ent, 22, (12 << 11) | (0 << 5) | 0)    # time 12:00
        struct.pack_into("<H", ent, 24, (46 << 9) | (7 << 5) | 11)    # date 2026-07-11
        struct.pack_into("<H", ent, 26, cluster & 0xFFFF)
        struct.pack_into("<I", ent, 28, len(data))
        buf += ent

    used = sum(len(make_vfat(n, to_83(n))) + 32 for n, _, _ in files)
    if used > ROOT_ENTRIES * 32:
        print(f"  WARNING: root dir overflow ({used} > {ROOT_ENTRIES * 32})")
    buf += b"\x00" * max(0, ROOT_ENTRIES * 32 - len(buf))
    return bytes(buf)


# ─── FAT Builder ──────────────────────────────────────────────────────────────

def build_fat(file_info):
    """
    Build the two FAT copies for the floppy.

    file_info: {name: (data, [cluster_nums])}
    Returns bytes (FAT_SIZE * 2).
    """
    entries = [0xFF0 | MEDIA_DESCRIPTOR, 0xFFF]
    entries.extend([0] * (TOTAL_CLUSTERS + 2 - len(entries)))

    for name, (data, clusters) in file_info.items():
        for i, c in enumerate(clusters):
            entries[c] = 0xFFF if i == len(clusters) - 1 else clusters[i + 1]

    # Pack 12-bit entries in pairs → 3 bytes
    raw = bytearray()
    i = 0
    while i < len(entries):
        e1 = entries[i] & 0xFFF
        if i + 1 < len(entries):
            e2 = entries[i + 1] & 0xFFF
            raw += struct.pack("BBB",
                               e1 & 0xFF,
                               ((e1 >> 8) & 0x0F) | ((e2 & 0x0F) << 4),
                               (e2 >> 4) & 0xFF)
            i += 2
        else:
            raw += struct.pack("<H", e1)[:2]
            i += 1

    fat = bytes(raw)[:FAT_SIZE].ljust(FAT_SIZE, b"\x00")
    return fat + fat  # two copies


# ─── Main Builder ─────────────────────────────────────────────────────────────

def build_floppy(files):
    """
    Build a complete 1.44MB FAT12 floppy image.

    files: list of (filename, bytes_data)
    Returns full 1_474_560-byte image.
    """
    img = bytearray(TOTAL_SECTORS * BYTES_PER_SECTOR)

    # Boot sector
    img[0:512] = make_bootsector()

    # Cluster allocation
    info = {}
    next_cluster = 2
    for name, data in files:
        n = max(1, math.ceil(len(data) / BYTES_PER_SECTOR))
        clusters = list(range(next_cluster, next_cluster + n))
        info[name] = (data, clusters)
        next_cluster += n

    assert next_cluster - 2 <= TOTAL_CLUSTERS, "floppy overflow!"

    # FATs
    fat = build_fat(info)
    fat_off = RESERVED_SECTORS * BYTES_PER_SECTOR
    img[fat_off:fat_off + len(fat)] = fat

    # Root directory (uses VFAT)
    root_data = build_root_dir([(n, d, info[n][1][0]) for n, d in files])
    root_off = (RESERVED_SECTORS + NUM_FATS * SECTORS_PER_FAT) * BYTES_PER_SECTOR
    img[root_off:root_off + len(root_data)] = root_data

    # File data
    data_off = FIRST_DATA_SECTOR * BYTES_PER_SECTOR
    for name, (data, clusters) in info.items():
        off = data_off + (clusters[0] - 2) * BYTES_PER_SECTOR
        img[off:off + len(data)] = data

    return bytes(img)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  FAT12 Floppy + VFAT Long Filenames")
    print("  For 99.hackclub.com Windows 98 emulator")
    print("=" * 60)
    print()

    files = []
    for fn in ["index.html", "guestbook.html"]:
        p = PROJECT_DIR / fn
        if p.exists():
            files.append((fn, p.read_bytes()))
            print(f"  + {fn} ({p.stat().st_size} bytes)")

    for fn in sorted(os.listdir(ASSETS_DIR)):
        if fn.lower().endswith(".gif"):
            p = ASSETS_DIR / fn
            files.append((fn, p.read_bytes()))
            print(f"  + {fn} ({p.stat().st_size} bytes)")

    if not files:
        print("  ERROR: no files found!")
        return

    img = build_floppy(files)
    with open(FLOPPY_PATH, "wb") as f:
        f.write(img)

    print(f"\n  Written: {FLOPPY_PATH.name} ({len(img):,} bytes)")
    print()
    print("=" * 60)
    print("  READY")
    print("=" * 60)
    print()
    print("  Use in 99.hackclub.com:")
    print()
    print("  Option A - Mount as floppy (BEST):")
    print("   1. Boot Windows 98")
    print("   2. Look for 'Floppy' / 'FDD' / 'Disk image' controls")
    print("      below the emulator screen")
    print("   3. Select titannet.img")
    print("   4. Open My Computer -> A: drive")
    print("   5. Files show with original names (VFAT long filenames)")
    print()
    print("  Option B - Send files directly (fallback):")
    print("   1. Click 'Send files to emulator' button below screen")
    print("   2. Select all 9 files (the .html + .gif files from assets/)")
    print("   3. They appear inside Win98 - check desktop or My Computer")
    print()
    print("  Files (all 9):")
    for n, _ in files:
        print(f"     {n}")


if __name__ == "__main__":
    main()
