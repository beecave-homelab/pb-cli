"""High-level selection logic for Linux-only pb-cli-linux."""
from __future__ import annotations

from enum import Enum
from typing import Union

from . import backends as be


class Backend(str, Enum):
    AUTO = "auto"
    PYCLIP = "pyclip"
    WL_CLIPBOARD = "wl-clipboard"
    TMUX = "tmux"
    FILE = "file"


BackendName = Union[Backend, str]  # accept enum or raw string


def _norm(backend: BackendName) -> str:
    """Normalize Backend/str into a plain lowercase string."""
    if isinstance(backend, Backend):
        return backend.value
    return str(backend)


def _choose_for_copy(preferred: BackendName = Backend.AUTO) -> str:
    b = _norm(preferred)
    if b != "auto":
        return b
    if be.pyclip_available():
        return "pyclip"
    if be.wl_available():
        return "wl-clipboard"
    if be.tmux_available():
        return "tmux"
    return "file"


def _choose_for_paste(preferred: BackendName = Backend.AUTO) -> str:
    b = _norm(preferred)
    if b != "auto":
        return b
    if be.pyclip_available():
        return "pyclip"
    if be.wl_available():
        return "wl-clipboard"
    if be.tmux_available():
        return "tmux"
    return "file"


def copy(text: str, backend: BackendName = Backend.AUTO) -> None:
    """Copy text using the chosen backend."""
    b = _choose_for_copy(backend)
    if b == "pyclip":
        be.pyclip_copy(text)
    elif b == "wl-clipboard":
        be.wl_copy(text)
    elif b == "tmux":
        be.tmux_copy(text)
    elif b == "file":
        be.file_copy(text)
    else:
        raise ValueError(f"Unknown backend: {backend}")


def paste(backend: BackendName = Backend.AUTO) -> str:
    """Paste text using the chosen backend."""
    b = _choose_for_paste(backend)
    if b == "pyclip":
        return be.pyclip_paste()
    if b == "wl-clipboard":
        return be.wl_paste()
    if b == "tmux":
        return be.tmux_paste()
    if b == "file":
        return be.file_paste()
    raise ValueError(f"Unknown backend: {backend}")
