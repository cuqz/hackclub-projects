"""错误指纹归一化 — Issue 4 + Council R1 Section 7。"""
import hashlib
import re

# ISO timestamp: 2026-04-28T10:30:00Z / 2026-04-28 10:30:00.123+08:00
_RE_ISO_TS = re.compile(
    r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:?\d{2}|Z)?'
)

# Unix timestamp (10/13位整数，前后有 timestamp/at/time 关键字)
_RE_UNIX_TS = re.compile(
    r'(?:timestamp|at|time)[=: ]+\d{10,13}',
    re.IGNORECASE,
)

# Unix 路径: /foo/bar/baz.py
_RE_UNIX_PATH = re.compile(r'/[\w/.\-]+')

# Windows 路径: C:\Users\foo\bar.py
_RE_WIN_PATH = re.compile(r'[A-Za-z]:\\[\w\\\.\-]+')

# PID
_RE_PID = re.compile(r'(?:pid\s*=?\s*\d+|PID\s+\d+|process\s+\d+)', re.IGNORECASE)

# 内存地址: 0x7fff1234abcd
_RE_ADDR = re.compile(r'0x[0-9a-fA-F]+', re.IGNORECASE)


def normalize(error_message: str) -> str:
    """剥离可变内容，返回归一化错误字符串。"""
    s = _RE_ISO_TS.sub('<TS>', error_message)
    s = _RE_UNIX_TS.sub('<TS>', s)
    s = _RE_PID.sub('<PID>', s)
    s = _RE_ADDR.sub('<ADDR>', s)
    s = _RE_WIN_PATH.sub('<PATH>', s)
    s = _RE_UNIX_PATH.sub('<PATH>', s)
    return s


def fingerprint(error_type: str, error_message: str) -> str:
    """返回 sha256 短摘要（前 12 位），基于 error_type::normalized(error_message)。"""
    normalized = normalize(error_message)
    raw = f"{error_type}::{normalized}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return digest[:12]
