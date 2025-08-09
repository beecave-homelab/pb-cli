"""High-level clipboard helpers picking the best backend.

Author: elvee
Date: 2025-08-09
"""
from __future__ import annotations

from typing import Literal

from . import backends as be

BackendName = Literal["auto", "osc52", "tmux", "pyperclip", "file"]


def _choose_for_copy(preferred: BackendName = "auto") -> BackendName:
    if preferred != "auto":
        return preferred
    if be.osc52_available():
        return "osc52"
    if be.tmux_available():
        return "tmux"
    if be.pyperclip_available():
        return "pyperclip"
    return "file"


def _choose_for_paste(preferred: BackendName = "auto") -> BackendName:
    if preferred != "auto":
        return preferred
    if be.tmux_available():
        return "tmux"
    if be.pyperclip_available():
        return "pyperclip"
    return "file"


def copy(text: str, backend: BackendName = "auto") -> None:
    """Copy text using the chosen backend."""
    b = _choose_for_copy(backend)
    if b == "osc52":
        be.osc52_copy(text)
    elif b == "tmux":
        be.tmux_copy(text)
    elif b == "pyperclip":
        be.pyperclip_copy(text)
    elif b == "file":
        be.file_copy(text)
    else:
        raise ValueError(f"Unknown backend: {backend}")


def paste(backend: BackendName = "auto") -> str:
    """Paste text using the chosen backend."""
    b = _choose_for_paste(backend)
    if b == "tmux":
        return be.tmux_paste()
    if b == "pyperclip":
        return be.pyperclip_paste()
    if b == "file":
        return be.file_paste()
    # OSC52 cannot read clipboard portably; fall back.
    return be.file_paste()
