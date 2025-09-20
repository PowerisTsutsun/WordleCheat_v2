# app.py
import json
import customtkinter as ctk
from tkinter import messagebox
from utils import resource_path, init_ctk
from gui import WordleSolverGUI

def main(theme=1):
    # init CustomTkinter global settings
    init_ctk()

    # load words
    try:
        with open(resource_path("words.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            words = [w for w in data.get("words", []) if isinstance(w, str) and len(w) == 5]
    except FileNotFoundError:
        messagebox.showerror("Error", "words.json not found!")
        return
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    root = ctk.CTk()
    root.geometry("520x780+200+80")
    root.minsize(460, 660)

    WordleSolverGUI(root, words, theme_idx=theme)
    root.mainloop()

if __name__ == "__main__":
    main(1)  # pick 1/2/3
