import asyncio
import shutil
import subprocess
from pathlib import Path

# Dev-machine fallback: the edge-tts CLI that ships in the user's venv.
_DEV_EDGE = Path.home() / "audiobook" / "venv" / "bin" / "edge-tts"


def _resolve_cli():
    """Find an edge-tts command line, or None."""
    found = shutil.which("edge-tts")
    if found:
        return [found]
    if _DEV_EDGE.exists():
        return [str(_DEV_EDGE)]
    return None


def synthesize_file(text_file, voice, rate, out_path):
    """Render text_file to out_path (MP3) with the given voice and rate.

    Prefers the edge_tts Python API (so a PyInstaller bundle is self-contained
    and needs no external edge-tts binary). If the package isn't importable
    (e.g. running from system Python in dev), falls back to the edge-tts CLI,
    preserving the original behavior. Either way, edge-tts streams audio from
    Microsoft's online service, so a network connection is required.
    """
    text_file = Path(text_file)
    out_path = Path(out_path)

    try:
        import edge_tts
    except ModuleNotFoundError:
        edge_tts = None

    if edge_tts is not None:
        text = text_file.read_text(errors="ignore")
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        asyncio.run(communicate.save(str(out_path)))
        return

    cli = _resolve_cli()
    if cli is None:
        raise RuntimeError(
            "edge-tts is not available. Install it with: pip install edge-tts"
        )
    result = subprocess.run(
        [*cli, "--voice", voice, f"--rate={rate}",
         "--file", str(text_file), "--write-media", str(out_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or "edge-tts failed")
