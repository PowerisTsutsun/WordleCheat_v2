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
            # Chun : store words uppercased so UI and solver can treat input consistently
            words = [w.upper() for w in data.get("words", []) if isinstance(w, str) and len(w) == 5]
    except FileNotFoundError:
        messagebox.showerror("Error", "words.json not found!")
        return
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    root = ctk.CTk()
    root.minsize(460, 660)

    # Chun : center the window on the screen so it feels more polished
    w, h = 520, 780
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

    WordleSolverGUI(root, words, theme_idx=theme)
    root.mainloop()

if __name__ == "__main__":
    main(1)  # pick 1/2/3
