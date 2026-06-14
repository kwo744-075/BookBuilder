import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from posixpath import join as ppjoin, dirname as pdirname


class _TextExtractor(HTMLParser):
    """Strip XHTML to readable text, inserting line breaks on block tags."""

    BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6",
             "tr", "section", "article", "blockquote"}
    SKIP = {"script", "style", "head"}

    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)

    def text(self):
        raw = "".join(self.parts)
        lines = [ln.strip() for ln in raw.splitlines()]
        out = []
        for ln in lines:
            if ln or (out and out[-1]):  # collapse runs of blank lines
                out.append(ln)
        return "\n".join(out).strip()


def _localname(tag):
    # Drop any XML namespace: '{ns}item' -> 'item'.
    return tag.rsplit("}", 1)[-1]


def epub_to_text(epub_path, txt_file):
    """Extract an EPUB's text into txt_file using only the stdlib.

    An EPUB is a ZIP: META-INF/container.xml points to the OPF package file,
    whose spine defines the reading order of the XHTML chapters. We read them
    in order and strip the markup to text. No extra Python dependency.
    """
    epub_path = Path(epub_path)
    txt_file = Path(txt_file)
    txt_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(epub_path) as z:
            container = ET.fromstring(z.read("META-INF/container.xml"))
            opf_path = None
            for el in container.iter():
                if _localname(el.tag) == "rootfile":
                    opf_path = el.get("full-path")
                    break
            if not opf_path:
                raise RuntimeError("EPUB is missing its package file (rootfile)")

            opf = ET.fromstring(z.read(opf_path))
            opf_dir = pdirname(opf_path)

            manifest = {}   # id -> href
            spine_ids = []  # ordered idrefs
            for el in opf.iter():
                name = _localname(el.tag)
                if name == "item":
                    manifest[el.get("id")] = el.get("href")
                elif name == "itemref":
                    spine_ids.append(el.get("idref"))

            chunks = []
            for sid in spine_ids:
                href = manifest.get(sid)
                if not href:
                    continue
                full = ppjoin(opf_dir, href) if opf_dir else href
                try:
                    raw = z.read(full)
                except KeyError:
                    continue
                parser = _TextExtractor()
                parser.feed(raw.decode("utf-8", errors="ignore"))
                chunk = parser.text()
                if chunk:
                    chunks.append(chunk)
    except (zipfile.BadZipFile, KeyError) as e:
        raise RuntimeError(f"Could not read .epub file: {e}")

    txt_file.write_text("\n\n".join(chunks), encoding="utf-8")
    return txt_file
