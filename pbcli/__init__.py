"""pb-cli-linux – Linux-only pbcopy/pbpaste.

Backends: pyclip, wl-clipboard, tmux, file.

Author: elvee
Date: 2025-08-09
"""
from . import backends, clipboard  # re-export for convenience

__all__ = ["backends", "clipboard"]
