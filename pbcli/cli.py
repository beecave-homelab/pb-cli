"""Typer-based CLI for pb-cli.

Provides console scripts: `pbcopy` and `pbpaste`.

Author: elvee
Date: 2025-08-09
"""
from __future__ import annotations

import sys
from typing import Literal

import typer

from .clipboard import copy as do_copy, paste as do_paste

BackendName = Literal["auto", "osc52", "tmux", "pyperclip", "file"]


def pbcopy(
    backend: BackendName = typer.Option(  # type: ignore[call-overload]
        "auto",
        "--backend",
        help="Select backend: auto|osc52|tmux|pyperclip|file (default: auto).",
        case_sensitive=False,
    ),
    trim_final_newline: bool = typer.Option(
        False,
        "--trim-final-newline",
        help="Trim a single trailing newline from input before copying.",
    ),
) -> None:
    """Read stdin and copy to clipboard via the selected backend."""
    data = sys.stdin.read()
    if trim_final_newline and data.endswith("\n"):
        data = data[:-1]
    do_copy(data, backend=backend)  # type: ignore[arg-type]


def pbpaste(
    backend: BackendName = typer.Option(  # type: ignore[call-overload]
        "auto",
        "--backend",
        help="Select backend: auto|tmux|pyperclip|file (default: auto).",
        case_sensitive=False,
    ),
) -> None:
    """Print clipboard contents using the selected backend."""
    out = do_paste(backend=backend)  # type: ignore[arg-type]
    sys.stdout.write(out)
    sys.stdout.flush()


def run_pbcopy() -> None:
    """Entry point for the `pbcopy` script."""
    typer.run(pbcopy)


def run_pbpaste() -> None:
    """Entry point for the `pbpaste` script."""
    typer.run(pbpaste)
