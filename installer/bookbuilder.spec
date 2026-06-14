# PyInstaller spec for BookBuilder (one-folder build).
# Build with:  python3 -m PyInstaller installer/bookbuilder.spec --noconfirm
#
# Bundles the GUI + the bookbuilder package + edge_tts (online TTS client)
# + tkinterdnd2 (drag-and-drop, incl. its tkdnd Tcl binaries).
# External, NOT bundled: the Microsoft Edge TTS service (needs internet) and
# pdftotext/poppler (optional, only for PDF input).

import os
from PyInstaller.utils.hooks import collect_all

# Spec lives in installer/; the app lives one level up.
ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

datas = []
binaries = []
hiddenimports = [
    "edge_tts",
    "bookbuilder.engine", "bookbuilder.pdf", "bookbuilder.docx",
    "bookbuilder.epub", "bookbuilder.voices", "bookbuilder.tts",
    "bookbuilder.desktop", "bookbuilder.version",
]

# Pull in package data files + binaries + submodules for these.
for pkg in ("tkinterdnd2", "edge_tts"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BookBuilder",
    console=False,          # GUI app: no terminal window
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="BookBuilder",
)
