"""Typer-based CLI for pb-cli-linux (pyclip-first).

Provides console scripts: `pb-cli` (grouped), plus `pbcopy` and `pbpaste`.

Author: elvee
Date: 2025-08-09
"""
from __future__ import annotations

import sys
from typing import Literal

import typer

from .clipboard import copy as do_copy, paste as do_paste

BackendName = Literal["auto", "pyclip", "wl-clipboard", "tmux", "file"]

app = typer.Typer(help="pb-cli-linux: Linux-only pbcopy/pbpaste (pyclip-first)", add_completion=False)


@app.command("copy")
def cmd_copy(
    backend: BackendName = typer.Option(
        "auto",
        "--backend",
        help="Backend: auto|pyclip|wl-clipboard|tmux|file (default: auto).",
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


@app.command("paste")
def cmd_paste(
    backend: BackendName = typer.Option(
        "auto",
        "--backend",
        help="Backend: auto|pyclip|wl-clipboard|tmux|file (default: auto).",
        case_sensitive=False,
    ),
) -> None:
    """Print clipboard contents via the selected backend."""
    out = do_paste(backend=backend)  # type: ignore[arg-type]
    sys.stdout.write(out)
    sys.stdout.flush()


def pbcopy(
    backend: BackendName = "auto",
    trim_final_newline: bool = False,
) -> None:
    data = sys.stdin.read()
    if trim_final_newline and data.endswith("\n"):
        data = data[:-1]
    do_copy(data, backend=backend)  # type: ignore[arg-type]


def pbpaste(
    backend: BackendName = "auto",
) -> None:
    out = do_paste(backend=backend)  # type: ignore[arg-type]
    sys.stdout.write(out)
    sys.stdout.flush()


def run_main() -> None:
    app()


def run_pbcopy() -> None:
    typer.run(pbcopy)


def run_pbpaste() -> None:
    typer.run(pbpaste)
