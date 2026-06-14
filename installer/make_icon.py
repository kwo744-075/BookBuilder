#!/usr/bin/env python3
"""Generate BookBuilder's placeholder icon (PNG + ICO) into assets/.

Run:  python3 installer/make_icon.py
Replace assets/bookbuilder.png with real artwork anytime; re-run to refresh ICO.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

SIZE = 256
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# Rounded background tile.
d.rounded_rectangle([8, 8, SIZE - 8, SIZE - 8], radius=40, fill=(38, 70, 130, 255))

# A simple open "book": two pages + a center spine.
d.polygon([(48, 70), (124, 90), (124, 196), (48, 176)], fill=(245, 245, 245, 255))
d.polygon([(208, 70), (132, 90), (132, 196), (208, 176)], fill=(225, 230, 240, 255))
d.line([(128, 88), (128, 196)], fill=(38, 70, 130, 255), width=6)

# A few "text" lines on each page.
for i, y in enumerate(range(108, 176, 18)):
    d.line([(60, y), (116, y + 3)], fill=(150, 160, 180, 255), width=4)
    d.line([(140, y + 3), (196, y)], fill=(150, 160, 180, 255), width=4)

png = ASSETS / "bookbuilder.png"
img.save(png)

ico = ASSETS / "bookbuilder.ico"
img.save(ico, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

print("wrote", png)
print("wrote", ico)
