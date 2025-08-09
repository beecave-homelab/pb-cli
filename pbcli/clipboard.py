"""High-level selection logic for Linux-only pb-cli-linux."""
from __future__ import annotations

from typing import Literal

from . import backends as be

BackendName = Literal["auto", "pyclip", "wl-clipboard", "tmux", "file"]


def _choose_for_copy(preferred: BackendName = "auto") -> BackendName:
    if preferred != "auto":
        return preferred
    if be.pyclip_available():
        return "pyclip"
    if be.wl_available():
        return "wl-clipboard"
    if be.tmux_available():
        return "tmux"
    return "file"


def _choose_for_paste(preferred: BackendName = "auto") -> BackendName:
    if preferred != "auto":
        return preferred
    if be.pyclip_available():
        return "pyclip"
    if be.wl_available():
        return "wl-clipboard"
    if be.tmux_available():
        return "tmux"
    return "file"


def copy(text: str, backend: BackendName = "auto") -> None:
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


def paste(backend: BackendName = "auto") -> str:
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
