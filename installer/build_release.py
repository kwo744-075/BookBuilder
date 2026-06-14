#!/usr/bin/env python3
"""BookBuilder Release Builder.

Cleans previous builds, runs PyInstaller, packages the one-folder build into a
versioned ZIP under releases/, and writes a filled Release Notes file.

Usage:
    python3 installer/build_release.py
"""
import datetime
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bookbuilder.version import __version__  # noqa: E402

BUILD = ROOT / "build"
DIST = ROOT / "dist"
RELEASES = ROOT / "releases"
SPEC = ROOT / "installer" / "bookbuilder.spec"
TEMPLATE = ROOT / "installer" / "RELEASE_NOTES_TEMPLATE.md"
APPNAME = "BookBuilder"


def platform_tag():
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def clean():
    print("• Cleaning previous build/ and dist/ ...")
    for path in (BUILD, DIST):
        if path.exists():
            shutil.rmtree(path)


def build():
    print("• Running PyInstaller ...")
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(SPEC),
         "--noconfirm", "--distpath", str(DIST), "--workpath", str(BUILD)],
        check=True,
    )


def package(plat):
    appdir = DIST / APPNAME
    if not appdir.exists():
        raise SystemExit(f"Build output not found: {appdir}")
    RELEASES.mkdir(exist_ok=True)
    zip_path = RELEASES / f"{APPNAME}-{__version__}-{plat}.zip"
    if zip_path.exists():
        zip_path.unlink()
    print(f"• Packaging -> {zip_path.name}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(appdir.rglob("*")):
            z.write(f, Path(APPNAME) / f.relative_to(appdir))
    return zip_path


def write_release_notes(zip_path, plat):
    notes = RELEASES / f"RELEASE_NOTES-{__version__}.md"
    template = TEMPLATE.read_text() if TEMPLATE.exists() else "# BookBuilder v{version}\n"
    filled = template.format(
        version=__version__,
        date=datetime.date.today().isoformat(),
        platform=plat,
        zip_name=zip_path.name,
    )
    notes.write_text(filled)
    print(f"• Release notes -> {notes.name}")
    return notes


def main():
    plat = platform_tag()
    print(f"=== Building BookBuilder v{__version__} ({plat}) ===")
    clean()
    build()
    zip_path = package(plat)
    notes = write_release_notes(zip_path, plat)
    size_mb = zip_path.stat().st_size / 1_000_000
    print("\n=== Done ===")
    print(f"  ZIP:   {zip_path}  ({size_mb:.1f} MB)")
    print(f"  Notes: {notes}")


if __name__ == "__main__":
    main()
