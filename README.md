# pb-cli-linux

Linux-only `pbcopy` / `pbpaste` that **just works in the CLI**, with or without a display.

**Backend order**
- `pbcopy`: **pyclip** → **wl-clipboard (wl-copy)** → **tmux** → **file**
- `pbpaste`: **pyclip** → **wl-clipboard (wl-paste)** → **tmux** → **file**

> We intentionally **do not** use `xclip`/`xsel`.  
> On Wayland, `pyclip` prefers `wl-clipboard`; if it fails (or no display), we fall back to tmux or a file cache.

## Optional system tools

While not strictly required, installing `wl-clipboard` and/or `tmux` improves UX:

```bash
# Wayland clipboard
sudo apt install wl-clipboard        # or dnf/pacman equivalent

# Tmux fallback (server-side clipboard)
sudo apt install tmux
```

## Install (with PDM)

```bash
pdm install
pdm run pb-cli --help
pdm run pbcopy --help
pdm run pbpaste --help
```

Or build & install:
```bash
pdm build
pip install dist/pb_cli_linux-*.whl
```

## Usage

```bash
# Copy (auto)
echo "Hello" | pbcopy

# Paste (auto)
pbpaste

# Force a backend
echo "Hello" | pbcopy --backend pyclip
pbpaste --backend tmux
```

## File cache

If nothing else is available, the clipboard is stored/read from:
`~/.local/share/pb-cli-linux/clipboard.txt` (UTF-8).

---

**Author:** elvee  
**Date:** 2025-08-09
