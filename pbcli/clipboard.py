"""High-level selection & fallback logic for Linux-only pb-cli-linux.

Backends (auto order):
  copy/paste: pyclip -> wl-clipboard -> tmux -> file

Behavior:
- If a backend is *forced* (CLI --backend), we try only that backend and raise on failure.
- If backend is "auto", we *attempt in order*, catching BackendError and falling through.
- `file` is always the last resort (unless a forced backend failed).

This fixes the case where `pyclip` imports fine but can't initialize
(e.g., it wants xclip): we now fallback automatically instead of crashing.
"""
from __future__ import annotations

from enum import Enum
from typing import Union, List, Tuple

from . import backends as be


class Backend(str, Enum):
    AUTO = "auto"
    PYCLIP = "pyclip"
    WL_CLIPBOARD = "wl-clipboard"
    TMUX = "tmux"
    FILE = "file"


BackendName = Union[Backend, str]  # accept enum or raw string


def _norm(backend: BackendName) -> str:
    """Normalize Backend/str into a plain string."""
    if isinstance(backend, Backend):
        return backend.value
    return str(backend)


def _auto_order_for_copy() -> List[str]:
    """Return a best-effort ordered list of backends for copy."""
    order: List[str] = []

    # pyclip first (may still fail at runtime — we'll catch and fallback)
    if be.pyclip_available():
        order.append("pyclip")

    # wayland tools if present
    if be.wl_available():
        order.append("wl-clipboard")

    # tmux if present
    if be.tmux_available():
        order.append("tmux")

    # file is always possible; ensure it's last
    order.append("file")
    return order


def _auto_order_for_paste() -> List[str]:
    """Return a best-effort ordered list of backends for paste."""
    order: List[str] = []

    if be.pyclip_available():
        order.append("pyclip")

    if be.wl_available():
        order.append("wl-clipboard")

    if be.tmux_available():
        order.append("tmux")

    order.append("file")
    return order


def _copy_with_backend(b: str, text: str) -> None:
    """Dispatch copy to a single backend name, raising BackendError on failure."""
    if b == "pyclip":
        be.pyclip_copy(text)
    elif b == "wl-clipboard":
        be.wl_copy(text)
    elif b == "tmux":
        be.tmux_copy(text)
    elif b == "file":
        be.file_copy(text)
    else:
        raise ValueError(f"Unknown backend: {b}")


def _paste_with_backend(b: str) -> str:
    """Dispatch paste to a single backend name, raising BackendError on failure."""
    if b == "pyclip":
        return be.pyclip_paste()
    if b == "wl-clipboard":
        return be.wl_paste()
    if b == "tmux":
        return be.tmux_paste()
    if b == "file":
        return be.file_paste()
    raise ValueError(f"Unknown backend: {b}")


def copy(text: str, backend: BackendName = Backend.AUTO) -> None:
    """Copy text, trying backends in order if backend == auto."""
    b_req = _norm(backend)

    # Forced backend: try once and surface the error.
    if b_req != "auto":
        _copy_with_backend(b_req, text)
        return

    errors: list[Tuple[str, Exception]] = []
    for b in _auto_order_for_copy():
        try:
            _copy_with_backend(b, text)
            return
        except Exception as exc:  # catch BackendError or subprocess errors
            errors.append((b, exc))
            continue

    # Should never happen because 'file' is last, but just in case:
    msgs = "; ".join(f"{b}: {e}" for b, e in errors)
    raise RuntimeError(f"All copy backends failed: {msgs}")


def paste(backend: BackendName = Backend.AUTO) -> str:
    """Paste text, trying backends in order if backend == auto."""
    b_req = _norm(backend)

    if b_req != "auto":
        return _paste_with_backend(b_req)

    errors: list[Tuple[str, Exception]] = []
    for b in _auto_order_for_paste():
        try:
            return _paste_with_backend(b)
        except Exception as exc:
            errors.append((b, exc))
            continue

    msgs = "; ".join(f"{b}: {e}" for b, e in errors)
    raise RuntimeError(f"All paste backends failed: {msgs}")
