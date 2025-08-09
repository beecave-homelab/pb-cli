"""Clipboard backends used by pb-cli.

Backends:
- OSC52: write to client clipboard via terminal escape sequence (copy-only).
- tmux: use tmux buffers for copy/paste (server-side; can forward to system clipboard).
- pyperclip: cross-platform clipboard library (requires a system provider on Linux).
- file: local cache file in ~/.local/share/pb-cli/clipboard.txt

Author: elvee
Date: 2025-08-09
"""
from __future__ import annotations

import base64
import os
import shutil
import subprocess
from pathlib import Path


CACHE_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "pb-cli"
CACHE_FILE = CACHE_DIR / "clipboard.txt"


class BackendError(RuntimeError):
    """Raised when a backend operation fails."""


# ---------- OSC52 (copy only) ----------
def osc52_available() -> bool:
    """Return True if writing OSC52 makes sense (a TTY is present)."""
    try:
        with open("/dev/tty", "wb"):
            return True
    except OSError:
        return False


def osc52_copy(text: str) -> None:
    """Copy text to the *client* clipboard using OSC52 escape codes.

    Writes to /dev/tty. Inside tmux, wraps the sequence for passthrough.
    """
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    osc = f"\033]52;c;{b64}"
    bel = "\a"
    st = "\033\"  # String Terminator

    if os.environ.get("TMUX"):
        payload = f"\033Ptmux;\033{osc}{bel}{st}"
    else:
        payload = f"{osc}{bel}"

    try:
        with open("/dev/tty", "wb", buffering=0) as tty:
            tty.write(payload.encode("utf-8", "replace"))
            tty.flush()
    except OSError as exc:
        raise BackendError(f"OSC52 write failed: {exc}") from exc


# ---------- tmux ----------
def _have_tmux() -> bool:
    return shutil.which("tmux") is not None


def tmux_available() -> bool:
    """Return True if tmux is available and responsive."""
    if not _have_tmux():
        return False
    try:
        subprocess.run(
            ["tmux", "display-message", "-p", "#{version}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def tmux_copy(text: str) -> None:
    """Copy text into tmux buffer (and forward to clipboard if configured)."""
    if not tmux_available():
        raise BackendError("tmux not available")
    try:
        subprocess.run(["tmux", "load-buffer", "-"], input=text.encode("utf-8"), check=True)
    except subprocess.CalledProcessError as exc:
        raise BackendError(f"tmux copy failed: {exc}") from exc


def tmux_paste() -> str:
    """Return text from the tmux buffer."""
    if not tmux_available():
        raise BackendError("tmux not available")
    try:
        out = subprocess.check_output(["tmux", "show-buffer"])
        return out.decode("utf-8", "replace")
    except subprocess.CalledProcessError as exc:
        raise BackendError(f"tmux paste failed: {exc}") from exc


# ---------- pyperclip ----------
def pyperclip_available() -> bool:
    try:
        import pyperclip  # noqa: F401
    except Exception:
        return False
    return True


def pyperclip_copy(text: str) -> None:
    try:
        import pyperclip
        pyperclip.copy(text)
    except Exception as exc:
        raise BackendError(f"pyperclip copy failed: {exc}") from exc


def pyperclip_paste() -> str:
    try:
        import pyperclip
        return pyperclip.paste()
    except Exception as exc:
        raise BackendError(f"pyperclip paste failed: {exc}") from exc


# ---------- file cache ----------
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
