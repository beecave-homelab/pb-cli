"""pb-cli – terminal-first pbcopy/pbpaste for SSH & headless.

Package import name: `pbcli` (repo is `pb-cli`).

Author: elvee
Date: 2025-08-09
"""
from . import backends, clipboard  # re-export for convenience

__all__ = ["backends", "clipboard"]
