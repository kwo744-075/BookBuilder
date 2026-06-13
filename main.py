import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import subprocess, threading, re

from bookbuilder.engine import prepare_book, split_chapters

BASE = Path.home() / "BookBuilder"
OUT = BASE / "audiobooks"
WORK = BASE / "_work_gui"
EDGE = Path.home() / "audiobook" / "venv" / "bin" / "edge-tts"

VOICE = "en-US-EricNeural"
RATE = "-10%"

OUT.mkdir(exist_ok=True)
WORK.mkdir(exist_ok=True)

root = tk.Tk()
root.title("BookBuilder")
root.geometry("760x560")

selected_file = tk.StringVar(root, "No book selected")
status = tk.StringVar(root, "Ready")
progress = tk.IntVar(root, 0)

def clean_title(path):
    return re.sub(r"[^a-zA-Z0-9 _.-]", "", Path(path).stem).strip()

def convert(book):
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
        status.set("Preparing book...")

        prepare_book(book, txt_file)

        chapters = split_chapters(txt_file, chapter_dir)
        total = len(chapters)

        for idx, (num, chapter) in enumerate(chapters, start=1):
            mp3 = out_dir / f"{num:02d} - Chapter {num}.mp3"
            status.set(f"Creating Chapter {num} of {total}...")

            if not mp3.exists() or mp3.stat().st_size < 10000:
                result = subprocess.run([
                    str(EDGE),
                    "--voice", VOICE,
                    f"--rate={RATE}",
                    "--file", str(chapter),
                    "--write-media", str(mp3)
                ], capture_output=True, text=True)

                if result.returncode != 0:
                    raise RuntimeError(result.stderr or result.stdout or "edge-tts failed")

            progress.set(int(idx / total * 100))

        status.set("Finished!")
        messagebox.showinfo("BookBuilder", f"Done!\n\nSaved to:\n{out_dir}")
        subprocess.run(["xdg-open", str(out_dir)])

    except Exception as e:
        status.set("Error")
        messagebox.showerror("BookBuilder Error", str(e))

def pick_book():
    filename = filedialog.askopenfilename(
        title="Select Book",
        filetypes=[("Books", "*.epub *.txt"), ("All Files", "*.*")]
    )
    if filename:
        selected_file.set(filename)
        status.set("Book selected. Click START CONVERSION.")

def start():
    book = selected_file.get()
    if book == "No book selected":
        messagebox.showwarning("BookBuilder", "Pick a book first.")
        return
    threading.Thread(target=convert, args=(book,), daemon=True).start()

def open_folder():
    subprocess.run(["xdg-open", str(OUT)])

tk.Label(root, text="BOOKBUILDER", font=("Arial", 30, "bold")).pack(pady=20)

tk.Label(root, textvariable=selected_file, wraplength=700).pack(pady=10)

tk.Button(root, text="Select Book", width=35, height=2, command=pick_book).pack(pady=6)
tk.Button(root, text="START CONVERSION", width=35, height=2, command=start).pack(pady=6)

ttk.Progressbar(root, orient="horizontal", length=560, mode="determinate",
                variable=progress, maximum=100).pack(pady=20)

tk.Label(root, textvariable=status, font=("Arial", 12)).pack(pady=10)

tk.Button(root, text="Open Audiobooks Folder", width=35, height=2, command=open_folder).pack(pady=6)
tk.Button(root, text="Exit", width=35, height=2, command=root.destroy).pack(pady=6)

root.mainloop()
