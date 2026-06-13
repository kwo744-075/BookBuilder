import tkinter as tk
from tkinter import messagebox
import subprocess
from pathlib import Path

VOICE_MAP = {
    "Eric":"en-US-EricNeural",
    "Andrew":"en-US-AndrewNeural",
    "Brian":"en-US-BrianNeural",
    "Christopher":"en-US-ChristopherNeural",
    "Ryan":"en-GB-RyanNeural"
}

PREVIEW_TEXT = """Mary had a little lamb,
its fleece was white as snow.

Welcome to BookBuilder.
"""

root=tk.Tk()
root.title("Voice Studio")
root.geometry("500x420")

title=tk.Label(
    root,
    text="VOICE STUDIO",
    font=("Arial",22,"bold")
)
title.pack(pady=15)

def preview(name):

    Path("previews").mkdir(exist_ok=True)

    with open("previews/sample.txt","w") as f:
        f.write(PREVIEW_TEXT)

    subprocess.run([
        "edge-tts",
        "--voice",
        VOICE_MAP[name],
        "--rate=-10%",
        "--file",
        "previews/sample.txt",
        "--write-media",
        f"previews/{name}.mp3"
    ])

    subprocess.run([
        "xdg-open",
        f"previews/{name}.mp3"
    ])

for voice in VOICE_MAP:

    frame=tk.Frame(root)
    frame.pack(fill="x",pady=5,padx=20)

    tk.Label(
        frame,
        text=voice,
        width=20,
        anchor="w"
    ).pack(side="left")

    tk.Button(
        frame,
        text="▶ Preview",
        command=lambda v=voice: preview(v)
    ).pack(side="right")

root.mainloop()
