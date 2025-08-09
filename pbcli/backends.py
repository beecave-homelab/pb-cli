"""Linux-only clipboard backends for pb-cli-linux (no X11 xclip/xsel).

Order of preference:
- pyclip (abstracts Wayland/X11 when possible)
- wl-clipboard (wl-copy/wl-paste)
- tmux (server buffer)
- file (local cache)

Author: elvee
Date: 2025-08-09
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


CACHE_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "pb-cli-linux"
CACHE_FILE = CACHE_DIR / "clipboard.txt"


class BackendError(RuntimeError):
    """Raised when a backend operation fails."""


# ---------- pyclip (preferred) ----------
def pyclip_available() -> bool:
    try:
        import pyclip  # noqa: F401
        return True
    except Exception:
        return False


def pyclip_copy(text: str) -> None:
    try:
        import pyclip
        pyclip.copy(text)
    except Exception as exc:
        raise BackendError(f"pyclip copy failed: {exc}") from exc


def pyclip_paste() -> str:
    try:
        import pyclip
        data = pyclip.paste(text=True)
        return data if isinstance(data, str) else ""
    except Exception as exc:
        raise BackendError(f"pyclip paste failed: {exc}") from exc


# ---------- wl-clipboard (Wayland) ----------
def wl_available() -> bool:
    return shutil.which("wl-copy") is not None and shutil.which("wl-paste") is not None


def wl_copy(text: str) -> None:
    try:
        subprocess.run(["wl-copy"], input=text.encode("utf-8"), check=True)
    except Exception as exc:
        raise BackendError(f"wl-copy failed: {exc}") from exc


def wl_paste() -> str:
    try:
        out = subprocess.check_output(["wl-paste", "--no-newline"])
        return out.decode("utf-8", "replace")
    except subprocess.CalledProcessError as exc:
        raise BackendError(f"wl-paste failed: {exc}") from exc


# ---------- tmux (server buffer) ----------
def tmux_available() -> bool:
    return shutil.which("tmux") is not None


def tmux_copy(text: str) -> None:
    if not tmux_available():
        raise BackendError("tmux not available")
    try:
        subprocess.run(["tmux", "load-buffer", "-"], input=text.encode("utf-8"), check=True)
    except subprocess.CalledProcessError as exc:
        raise BackendError(f"tmux copy failed: {exc}") from exc


def tmux_paste() -> str:
    if not tmux_available():
        raise BackendError("tmux not available")
    try:
        out = subprocess.check_output(["tmux", "show-buffer"])
        return out.decode("utf-8", "replace")
    except subprocess.CalledProcessError as exc:
        raise BackendError(f"tmux paste failed: {exc}") from exc


# ---------- file (local cache) ----------
def file_available() -> bool:
    return True


def file_copy(text: str) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise BackendError(f"file cache copy failed: {exc}") from exc


def file_paste() -> str:
    try:
        return CACHE_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except OSError as exc:
        raise BackendError(f"file cache paste failed: {exc}") from exc
