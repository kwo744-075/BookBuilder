import os
import sys
import subprocess
from pathlib import Path


def open_path(path):
    """Open a file or folder with the OS default handler (cross-platform)."""
    path = str(path)
    if sys.platform.startswith("win"):
        os.startfile(path)  # noqa: S606 (Windows-only)
    elif sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])
