import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# WordprocessingML namespace used inside word/document.xml.
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def docx_to_text(docx_path, txt_file):
    """Extract text from a .docx into txt_file using only the stdlib.

    A .docx is a ZIP whose word/document.xml holds the body. We read the
    text runs (w:t) and treat each paragraph (w:p) as a line, so no extra
    Python dependency is required. Returns the path to the written file.
    """
    docx_path = Path(docx_path)
    txt_file = Path(txt_file)
    txt_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(docx_path) as z:
            document_xml = z.read("word/document.xml")
    except (zipfile.BadZipFile, KeyError) as e:
        raise RuntimeError(f"Could not read .docx file: {e}")

    root = ET.fromstring(document_xml)

    lines = []
    for para in root.iter(f"{W_NS}p"):
        runs = [node.text for node in para.iter(f"{W_NS}t") if node.text]
        lines.append("".join(runs))

    txt_file.write_text("\n".join(lines), encoding="utf-8")
    return txt_file
