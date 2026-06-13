import subprocess
from pathlib import Path

def test_conversion():

    Path("previews").mkdir(exist_ok=True)

    text = """Welcome to BookBuilder.

This is a successful conversion test.
"""

    sample = Path("previews") / "test.txt"

    sample.write_text(text)

    output = Path("previews") / "test.mp3"

    subprocess.run([
        "edge-tts",
        "--voice",
        "en-US-EricNeural",
        "--rate=-10%",
        "--file",
        str(sample),
        "--write-media",
        str(output)
    ])

    return output
