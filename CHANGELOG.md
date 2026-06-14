# Changelog

All notable changes to BookBuilder are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.1] - 2026-06-14

First packaged & distributed release. Same application as 1.0.0, now shipped as
Windows and Linux installers built via CI.

### Added
- Windows installer (Inno Setup) and Linux `.deb` + AppImage published as
  GitHub Release assets through the automated workflow.

## [1.0.0] - 2026-06-14

### Added
- **Distribution system**: PyInstaller bundle, automated Release Builder
  (`installer/build_release.py`), Linux `.deb` + AppImage installers, Windows
  Inno Setup installer, and a GitHub Actions release workflow.
- **EPUB support** — read `.epub` books (stdlib OPF/spine parser).
- **Multi-book queue** — add several books; they convert sequentially.
- **Per-book "Save As"** output naming.
- **Drag-and-drop** book selection (optional, via tkinterdnd2).
- **Voice speed control** (0.75×–1.5×).
- **Three female voices** (Aria, Jenny, Sonia — Sonia is British).
- **Play Sample** button to preview a voice.
- **%/elapsed/ETA** progress line and a session "books converted" counter.
- App **version label** and reproducible **placeholder icon**.

### Changed
- Extracted conversion logic into the `bookbuilder` package (engine, tts,
  pdf, docx, epub, voices, desktop, version).
- TTS now uses the `edge_tts` Python API when bundled, with a CLI fallback.
- File-opening is cross-platform (`open_path`), no longer Linux-only.

### Fixed
- Crash when the source text was never copied into the work folder
  (`book.txt` not found).
- `.epub` files erroring as "unsupported format" despite being selectable.

## [0.2.0]

### Added
- PDF and DOCX input support.
- Voice selection dropdown.

## [0.1.0]

### Added
- Initial GUI: select a `.txt` book, convert chapters to MP3, progress bar.
