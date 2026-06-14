#!/usr/bin/env bash
# Build a .deb from the PyInstaller one-folder bundle in dist/BookBuilder.
# Declares poppler-utils as a dependency so PDF input works after `apt install`.
#
# Usage:  bash installer/linux/build_deb.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

VERSION="$(python3 -c 'from bookbuilder.version import __version__; print(__version__)')"
BUNDLE="$ROOT/dist/BookBuilder"
[ -d "$BUNDLE" ] || { echo "Bundle missing; run: python3 installer/build_release.py"; exit 1; }

PKG="$ROOT/build/deb/bookbuilder_${VERSION}_amd64"
rm -rf "$PKG"
mkdir -p "$PKG/DEBIAN" \
         "$PKG/opt/bookbuilder" \
         "$PKG/usr/bin" \
         "$PKG/usr/share/applications" \
         "$PKG/usr/share/icons/hicolor/256x256/apps"

# App payload
cp -r "$BUNDLE/." "$PKG/opt/bookbuilder/"

# Launcher on PATH
cat > "$PKG/usr/bin/bookbuilder" <<'EOF'
#!/bin/sh
exec /opt/bookbuilder/BookBuilder "$@"
EOF
chmod 755 "$PKG/usr/bin/bookbuilder"

# Desktop entry + icon
cp "$ROOT/assets/bookbuilder.png" "$PKG/usr/share/icons/hicolor/256x256/apps/bookbuilder.png"
cat > "$PKG/usr/share/applications/bookbuilder.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=BookBuilder
Comment=Convert ebooks (txt/pdf/docx/epub) into MP3 audiobooks
Exec=bookbuilder
Icon=bookbuilder
Terminal=false
Categories=AudioVideo;Audio;Utility;
EOF

# Control metadata
cat > "$PKG/DEBIAN/control" <<EOF
Package: bookbuilder
Version: ${VERSION}
Section: sound
Priority: optional
Architecture: amd64
Depends: poppler-utils
Maintainer: BookBuilder <noreply@example.com>
Description: Convert ebooks to audiobooks
 BookBuilder turns .txt/.pdf/.docx/.epub books into MP3 audiobooks using
 online neural voices. Requires an internet connection for voice synthesis.
EOF

mkdir -p "$ROOT/releases"
OUT="$ROOT/releases/bookbuilder_${VERSION}_amd64.deb"
dpkg-deb --build --root-owner-group "$PKG" "$OUT"
echo "Built: $OUT"
