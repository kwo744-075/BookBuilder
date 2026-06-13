import shutil
import subprocess
from pathlib import Path


def pdf_to_text(pdf_path, txt_file):
    """Extract a PDF's text into txt_file using the pdftotext CLI (poppler).

    Mirrors how the app already shells out to edge-tts, so no extra Python
    dependency is required. Returns the path to the written text file.
    """
    pdf_path = Path(pdf_path)
    txt_file = Path(txt_file)
    txt_file.parent.mkdir(parents=True, exist_ok=True)

    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        raise RuntimeError(
            "pdftotext is not installed. Install it with:\n"
            "    sudo apt install poppler-utils"
        )

    result = subprocess.run(
        [pdftotext, str(pdf_path), str(txt_file)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or "pdftotext failed")

    return txt_file
