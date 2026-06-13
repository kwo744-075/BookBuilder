import re
import shutil
from pathlib import Path

from .pdf import pdf_to_text
from .docx import docx_to_text


def prepare_book(src_path, txt_file):
    """Copy the selected book into its work folder as plain text (book.txt).

    Ensures the work folder exists and that the source text the rest of the
    pipeline reads is actually present. Returns the path to the prepared file.
    """
    src_path = Path(src_path)
    txt_file = Path(txt_file)
    txt_file.parent.mkdir(parents=True, exist_ok=True)

    suffix = src_path.suffix.lower()
    if suffix == ".txt":
        shutil.copy(src_path, txt_file)
    elif suffix == ".pdf":
        pdf_to_text(src_path, txt_file)
    elif suffix == ".docx":
        docx_to_text(src_path, txt_file)
    else:
        raise RuntimeError(
            f"Unsupported book format: '{src_path.suffix}'. "
            "Please select a .txt, .pdf, or .docx file."
        )

    return txt_file


def split_chapters(txt_path, chapter_dir):
    chapter_dir.mkdir(parents=True, exist_ok=True)
    for f in chapter_dir.glob("chapter_*.txt"):
        f.unlink()

    lines = txt_path.read_text(errors="ignore").splitlines()
    chapter_re = re.compile(r"^\s*Chapter\s+(\d+)\s*$", re.I)

    chapters = []
    current = None

    for line in lines:
        m = chapter_re.match(line)
        if m:
            num = int(m.group(1))
            current = chapter_dir / f"chapter_{num:02d}.txt"
            current.write_text(line + "\n", encoding="utf-8")
            chapters.append((num, current))
        elif current:
            with current.open("a", encoding="utf-8") as out:
                out.write(line + "\n")

    if not chapters:
        current = chapter_dir / "chapter_01.txt"
        shutil.copy(txt_path, current)
        chapters.append((1, current))

    return chapters
