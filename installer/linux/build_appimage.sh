#!/usr/bin/env bash
# Build a portable AppImage from the PyInstaller bundle in dist/BookBuilder.
#
# Usage:  bash installer/linux/build_appimage.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

VERSION="$(python3 -c 'from bookbuilder.version import __version__; print(__version__)')"
BUNDLE="$ROOT/dist/BookBuilder"
[ -d "$BUNDLE" ] || { echo "Bundle missing; run: python3 installer/build_release.py"; exit 1; }

APPDIR="$ROOT/build/AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp -r "$BUNDLE/." "$APPDIR/usr/bin/"

# Icon + desktop entry at AppDir root (required by appimagetool).
cp "$ROOT/assets/bookbuilder.png" "$APPDIR/bookbuilder.png"
cat > "$APPDIR/bookbuilder.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=BookBuilder
Comment=Convert ebooks (txt/pdf/docx/epub) into MP3 audiobooks
Exec=BookBuilder
Icon=bookbuilder
Terminal=false
Categories=AudioVideo;Audio;Utility;
EOF

# Entry point.
cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/BookBuilder" "$@"
EOF
chmod 755 "$APPDIR/AppRun"

# Fetch appimagetool if needed.
TOOL="$ROOT/build/appimagetool-x86_64.AppImage"
if [ ! -x "$TOOL" ]; then
  echo "Downloading appimagetool ..."
  curl -fsSL -o "$TOOL" \
    https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
  chmod +x "$TOOL"
fi

mkdir -p "$ROOT/releases"
OUT="$ROOT/releases/BookBuilder-${VERSION}-x86_64.AppImage"
# --appimage-extract-and-run avoids needing FUSE (works in CI/containers).
ARCH=x86_64 "$TOOL" --appimage-extract-and-run "$APPDIR" "$OUT"
echo "Built: $OUT"
