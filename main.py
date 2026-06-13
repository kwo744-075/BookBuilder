import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from pathlib import Path
import subprocess, threading, re, time

from bookbuilder.engine import prepare_book, split_chapters
from bookbuilder.voices import VOICE_MAP, DEFAULT_VOICE, SPEED_MAP, DEFAULT_SPEED

# Drag-and-drop is optional: if tkinterdnd2 isn't available the app still
# runs normally and the Select Book button keeps working.
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

BASE = Path.home() / "BookBuilder"
OUT = BASE / "audiobooks"
WORK = BASE / "_work_gui"
PREVIEW = BASE / "previews"
EDGE = Path.home() / "audiobook" / "venv" / "bin" / "edge-tts"

SAMPLE_TEXT = (
    "Thank you for choosing BookBuilder. "
    "Here is a sample sound of what your voice will sound like."
)

OUT.mkdir(exist_ok=True)
WORK.mkdir(exist_ok=True)

root = TkinterDnD.Tk() if DND_AVAILABLE else tk.Tk()
root.title("BookBuilder")
root.geometry("760x660")

book_queue = []        # list of (source_path, output_name), processed top-to-bottom
queue_running = False  # guard so the queue can't be started twice
status = tk.StringVar(root, "Ready")
progress = tk.IntVar(root, 0)
pct_time = tk.StringVar(root, "")
voice_choice = tk.StringVar(root, DEFAULT_VOICE)
speed_choice = tk.StringVar(root, DEFAULT_SPEED)

books_done = 0
converted = tk.StringVar(root, "Books converted: 0")

def sanitize(name):
    # Keep filesystem-safe characters only; used for output folder names.
    return re.sub(r"[^a-zA-Z0-9 _.-]", "", name).strip()

def clean_title(path):
    return sanitize(Path(path).stem)

def fmt_time(seconds):
    seconds = int(seconds)
    return f"{seconds // 60}:{seconds % 60:02d}"

def convert(book, voice, rate, out_name, notify=True):
    global books_done
    try:
        book = Path(book)
        title = sanitize(out_name) or clean_title(book)
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
                    f"--rate={rate}",
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
        books_done += 1
        converted.set(f"Books converted: {books_done}")
        if notify:
            messagebox.showinfo("BookBuilder", f"Done!\n\nSaved to:\n{out_dir}")
            subprocess.run(["xdg-open", str(out_dir)])

    except Exception as e:
        status.set("Error")
        messagebox.showerror("BookBuilder Error", str(e))

def enqueue(path):
    out_name = clean_title(path)  # default; user can change via Save As
    book_queue.append((path, out_name))
    book_list.insert("end", out_name)
    status.set(f"{len(book_queue)} book(s) in queue. Use Save As to rename, then START QUEUE.")

def save_as():
    if queue_running:
        return
    sel = book_list.curselection()
    if not sel:
        messagebox.showinfo("BookBuilder", "Select a book in the queue first.")
        return
    i = sel[0]
    path, out_name = book_queue[i]
    new_name = simpledialog.askstring(
        "Save book as", "Output name for this book:", initialvalue=out_name)
    if new_name is None:
        return
    new_name = sanitize(new_name)
    if not new_name:
        messagebox.showwarning("BookBuilder", "Please enter a valid name.")
        return
    book_queue[i] = (path, new_name)
    book_list.delete(i)
    book_list.insert(i, new_name)
    book_list.selection_set(i)

def add_books():
    filenames = filedialog.askopenfilenames(
        title="Select Book(s)",
        filetypes=[("Books", "*.pdf *.docx *.txt *.epub"), ("All Files", "*.*")]
    )
    for f in filenames:
        enqueue(f)

def on_drop(event):
    for path in root.tk.splitlist(event.data):
        enqueue(path)

def clear_queue():
    if queue_running:
        return
    book_queue.clear()
    book_list.delete(0, "end")
    status.set("Queue cleared.")

def start_queue():
    global queue_running
    if queue_running:
        return
    if not book_queue:
        messagebox.showwarning("BookBuilder", "Add at least one book first.")
        return
    voice = VOICE_MAP.get(voice_choice.get(), VOICE_MAP[DEFAULT_VOICE])
    rate = SPEED_MAP.get(speed_choice.get(), SPEED_MAP[DEFAULT_SPEED])
    queue_running = True
    threading.Thread(target=run_queue, args=(voice, rate), daemon=True).start()

def run_queue(voice, rate):
    # One worker drains the queue top-to-bottom, so books never overlap.
    global queue_running
    done = 0
    try:
        while book_queue:
            book, out_name = book_queue[0]
            done += 1
            status.set(f"Book {done} ({len(book_queue)} left): {out_name}")
            convert(book, voice, rate, out_name, notify=False)
            book_queue.pop(0)
            book_list.delete(0)
        status.set(f"Queue finished! {done} book(s) done.")
        messagebox.showinfo("BookBuilder", f"Queue complete!\n\n{done} book(s) converted.")
        subprocess.run(["xdg-open", str(OUT)])
    finally:
        queue_running = False

def play_sample():
    voice_name = voice_choice.get()
    voice = VOICE_MAP.get(voice_name, VOICE_MAP[DEFAULT_VOICE])
    rate = SPEED_MAP.get(speed_choice.get(), SPEED_MAP[DEFAULT_SPEED])

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
                f"--rate={rate}",
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

tk.Label(root, text="Queue — output names (select one, then Save As to rename):").pack(pady=(6, 2))
book_list = tk.Listbox(root, width=72, height=6)
book_list.pack()

if DND_AVAILABLE:
    tk.Label(root, text="(or drag & drop book(s) anywhere on this window)",
             fg="gray").pack()
    root.drop_target_register(DND_FILES)
    root.dnd_bind("<<Drop>>", on_drop)

queue_btns = tk.Frame(root)
queue_btns.pack(pady=6)
tk.Button(queue_btns, text="Add Book(s)", width=16, height=2,
          command=add_books).pack(side="left", padx=4)
tk.Button(queue_btns, text="Save As…", width=14, height=2,
          command=save_as).pack(side="left", padx=4)
tk.Button(queue_btns, text="Clear Queue", width=14, height=2,
          command=clear_queue).pack(side="left", padx=4)

voice_frame = tk.Frame(root)
voice_frame.pack(pady=6)

tk.Label(voice_frame, text="Speed:").pack(side="left")
ttk.Combobox(voice_frame, textvariable=speed_choice, values=list(SPEED_MAP.keys()),
             state="readonly", width=6).pack(side="left", padx=(2, 10))

tk.Label(voice_frame, text="Voice:").pack(side="left")
ttk.Combobox(voice_frame, textvariable=voice_choice, values=list(VOICE_MAP.keys()),
             state="readonly", width=22).pack(side="left", padx=2)

tk.Button(voice_frame, text="▶ Play Sample", command=play_sample).pack(side="left", padx=6)

tk.Button(root, text="START QUEUE", width=35, height=2, command=start_queue).pack(pady=6)

ttk.Progressbar(root, orient="horizontal", length=560, mode="determinate",
                variable=progress, maximum=100).pack(pady=(20, 4))

tk.Label(root, textvariable=pct_time, font=("Arial", 11)).pack()

tk.Label(root, textvariable=status, font=("Arial", 12)).pack(pady=10)

tk.Button(root, text="Open Audiobooks Folder", width=35, height=2, command=open_folder).pack(pady=6)
tk.Button(root, text="Exit", width=35, height=2, command=root.destroy).pack(pady=6)

# Corner overlays (place() so they don't disturb the packed layout above)
tk.Label(root, textvariable=converted, fg="gray").place(relx=1.0, rely=0.0,
                                                         anchor="ne", x=-10, y=8)
tk.Label(root, text="v1.0", fg="gray").place(relx=1.0, rely=1.0,
                                             anchor="se", x=-10, y=-8)

root.mainloop()
