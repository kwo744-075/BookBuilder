import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import subprocess, threading, re, time

from bookbuilder.engine import prepare_book, split_chapters
from bookbuilder.voices import VOICE_MAP, DEFAULT_VOICE

BASE = Path.home() / "BookBuilder"
OUT = BASE / "audiobooks"
WORK = BASE / "_work_gui"
PREVIEW = BASE / "previews"
EDGE = Path.home() / "audiobook" / "venv" / "bin" / "edge-tts"

RATE = "-10%"
SAMPLE_TEXT = (
    "Thank you for choosing BookBuilder. "
    "Here is a sample sound of what your voice will sound like."
)

OUT.mkdir(exist_ok=True)
WORK.mkdir(exist_ok=True)

root = tk.Tk()
root.title("BookBuilder")
root.geometry("760x560")

selected_file = tk.StringVar(root, "No book selected")
status = tk.StringVar(root, "Ready")
progress = tk.IntVar(root, 0)
pct_time = tk.StringVar(root, "")
voice_choice = tk.StringVar(root, DEFAULT_VOICE)

def clean_title(path):
    return re.sub(r"[^a-zA-Z0-9 _.-]", "", Path(path).stem).strip()

def fmt_time(seconds):
    seconds = int(seconds)
    return f"{seconds // 60}:{seconds % 60:02d}"

def convert(book, voice):
    try:
        book = Path(book)
        title = clean_title(book)
        out_dir = OUT / title
        work_dir = WORK / title
        chapter_dir = work_dir / "chapters"
        txt_file = work_dir / "book.txt"

        out_dir.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=True, exist_ok=True)

        progress.set(0)
        pct_time.set("0%  •  0:00 elapsed")
        status.set("Preparing book...")

        prepare_book(book, txt_file)

        chapters = split_chapters(txt_file, chapter_dir)
        total = len(chapters)
        start_time = time.time()

        for idx, (num, chapter) in enumerate(chapters, start=1):
            mp3 = out_dir / f"{num:02d} - Chapter {num}.mp3"
            status.set(f"Creating Chapter {num} of {total}...")

            if not mp3.exists() or mp3.stat().st_size < 10000:
                result = subprocess.run([
                    str(EDGE),
                    "--voice", voice,
                    f"--rate={RATE}",
                    "--file", str(chapter),
                    "--write-media", str(mp3)
                ], capture_output=True, text=True)

                if result.returncode != 0:
                    raise RuntimeError(result.stderr or result.stdout or "edge-tts failed")

            progress.set(int(idx / total * 100))

            elapsed = time.time() - start_time
            eta = elapsed / idx * (total - idx)
            pct_time.set(
                f"{int(idx / total * 100)}%  •  {fmt_time(elapsed)} elapsed  •  ~{fmt_time(eta)} left"
            )

        status.set("Finished!")
        pct_time.set(f"100%  •  done in {fmt_time(time.time() - start_time)}")
        messagebox.showinfo("BookBuilder", f"Done!\n\nSaved to:\n{out_dir}")
        subprocess.run(["xdg-open", str(out_dir)])

    except Exception as e:
        status.set("Error")
        messagebox.showerror("BookBuilder Error", str(e))

def pick_book():
    filename = filedialog.askopenfilename(
        title="Select Book",
        filetypes=[("Books", "*.pdf *.txt *.epub"), ("All Files", "*.*")]
    )
    if filename:
        selected_file.set(filename)
        status.set("Book selected. Click START CONVERSION.")

def start():
    book = selected_file.get()
    if book == "No book selected":
        messagebox.showwarning("BookBuilder", "Pick a book first.")
        return
    voice = VOICE_MAP.get(voice_choice.get(), VOICE_MAP[DEFAULT_VOICE])
    threading.Thread(target=convert, args=(book, voice), daemon=True).start()

def play_sample():
    voice_name = voice_choice.get()
    voice = VOICE_MAP.get(voice_name, VOICE_MAP[DEFAULT_VOICE])

    def run():
        try:
            PREVIEW.mkdir(parents=True, exist_ok=True)
            sample_txt = PREVIEW / "sample.txt"
            sample_txt.write_text(SAMPLE_TEXT, encoding="utf-8")
            sample_mp3 = PREVIEW / f"{voice_name}.mp3"

            status.set(f"Generating {voice_name} sample...")
            result = subprocess.run([
                str(EDGE),
                "--voice", voice,
                f"--rate={RATE}",
                "--file", str(sample_txt),
                "--write-media", str(sample_mp3)
            ], capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(result.stderr or result.stdout or "edge-tts failed")

            status.set(f"Playing {voice_name} sample...")
            subprocess.run(["xdg-open", str(sample_mp3)])
            status.set("Ready")

        except Exception as e:
            status.set("Error")
            messagebox.showerror("BookBuilder Error", str(e))

    threading.Thread(target=run, daemon=True).start()

def open_folder():
    subprocess.run(["xdg-open", str(OUT)])

tk.Label(root, text="BOOKBUILDER", font=("Arial", 30, "bold")).pack(pady=20)

tk.Label(root, textvariable=selected_file, wraplength=700).pack(pady=10)

tk.Button(root, text="Select Book", width=35, height=2, command=pick_book).pack(pady=6)

tk.Label(root, text="Voice:").pack()
voice_frame = tk.Frame(root)
voice_frame.pack(pady=6)
ttk.Combobox(voice_frame, textvariable=voice_choice, values=list(VOICE_MAP.keys()),
             state="readonly", width=28).pack(side="left")
tk.Button(voice_frame, text="▶ Play Sample", command=play_sample).pack(side="left", padx=6)

tk.Button(root, text="START CONVERSION", width=35, height=2, command=start).pack(pady=6)

ttk.Progressbar(root, orient="horizontal", length=560, mode="determinate",
                variable=progress, maximum=100).pack(pady=(20, 4))

tk.Label(root, textvariable=pct_time, font=("Arial", 11)).pack()

tk.Label(root, textvariable=status, font=("Arial", 12)).pack(pady=10)

tk.Button(root, text="Open Audiobooks Folder", width=35, height=2, command=open_folder).pack(pady=6)
tk.Button(root, text="Exit", width=35, height=2, command=root.destroy).pack(pady=6)

root.mainloop()
