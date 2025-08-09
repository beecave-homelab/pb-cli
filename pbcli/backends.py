"""Linux-only clipboard backends for pb-cli-linux (quiet fallbacks).

Order of preference (auto):
- pyclip (abstracts Wayland/X11 when possible)
- wl-clipboard (wl-copy/wl-paste)  [only if Wayland socket exists]
- tmux (server buffer)             [only if a tmux server is responsive]
- file (local cache)

All subprocess calls suppress stderr to avoid noisy error messages when a
display or tmux server is not present.
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
def _wayland_socket_exists() -> bool:
    display = os.environ.get("WAYLAND_DISPLAY")
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime and display:
        if (Path(runtime) / display).exists():
            return True
    # Common default socket name if env var is missing
    if runtime:
        if any(Path(runtime).glob("wayland-*")):
            return True
    return False


def wl_available() -> bool:
    return (
        shutil.which("wl-copy") is not None
        and shutil.which("wl-paste") is not None
        and _wayland_socket_exists()
    )


def wl_copy(text: str) -> None:
    try:
        subprocess.run(
            ["wl-copy"],
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        raise BackendError(f"wl-copy failed: {exc}") from exc


def wl_paste() -> str:
    try:
        out = subprocess.check_output(
            ["wl-paste", "--no-newline"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8", "replace")
    except subprocess.CalledProcessError as exc:
        raise BackendError(f"wl-paste failed: {exc}") from exc


# ---------- tmux (server buffer) ----------
def tmux_available() -> bool:
    if shutil.which("tmux") is None:
        return False
    try:
        subprocess.run(
            ["tmux", "display-message", "-p", "#{version}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=0.5,
        )
        return True
    except Exception:
        return False


def tmux_copy(text: str) -> None:
    if not tmux_available():
        raise BackendError("tmux server not available")
    try:
        subprocess.run(
            ["tmux", "load-buffer", "-"],
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise BackendError(f"tmux copy failed: {exc}") from exc


def tmux_paste() -> str:
    if not tmux_available():
        raise BackendError("tmux server not available")
    try:
        out = subprocess.check_output(
            ["tmux", "show-buffer"],
            stderr=subprocess.DEVNULL,
        )
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
