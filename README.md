# pb-cli

Terminal-first substitutes for `pbcopy` / `pbpaste` that work **great over SSH** and **without a display**.

**Backend order**
- `pbcopy`: **OSC52** → **tmux** → **pyperclip** → **file**
- `pbpaste`: **tmux** → **pyperclip** → **file** (OSC52 read is intentionally disabled)

> OSC52 writes to the **client** clipboard (your local terminal) via escape codes — ideal over SSH.
> In **tmux**, enable:  
> `set -g allow-passthrough on` and `set -g set-clipboard on`

## Install (with PDM)

```bash
pdm install
pdm run pbcopy --help
pdm run pbpaste --help
```

Or build & install:
```bash
pdm build
pip install dist/pb_cli-*.whl
```

## Usage

```bash
# Copy (auto)
echo "Hello" | pbcopy

# Paste (auto)
pbpaste

# Force a backend
echo "Hello" | pbcopy --backend osc52
pbpaste --backend tmux
```

## Notes

- **OSC52**: Writes to `/dev/tty`. Inside tmux we wrap the sequence for passthrough.
- **tmux**: Requires `tmux` in `$PATH`. With `set-clipboard on`, tmux forwards to the terminal clipboard.
- **pyperclip**: Uses system providers (`wl-clipboard`, `xclip`, etc.). If none exist, pb-cli falls back to file.
- **file**: Cache path is `~/.local/share/pb-cli/clipboard.txt` (UTF-8).

---

**Author:** elvee  
**Date:** 2025-08-09
