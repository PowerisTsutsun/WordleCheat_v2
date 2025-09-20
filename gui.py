# gui.py
import sys
from effects import enable_glass
import datetime, random
import customtkinter as ctk
from tkinter import messagebox
from widgets import ElevatedKey
from palettes import PALETTES
from solver import filter_words


class WordleSolverGUI:
    FONT_LARGE  = ("Inter", 26, "bold")
    FONT_DISPLAY= ("Inter", 44, "bold")
    FONT_SMALL  = ("Inter", 12)
    FONT_KEY    = ("Inter", 20, "bold")

    def __init__(self, master, words, theme_idx=1):
        self.root = master
        self.words = [w.upper() for w in words]
        self.max_attempts = 6
        self.theme_idx = theme_idx

        self._bind_state()
        self.pal = PALETTES[self.theme_idx]
        self.glass = (theme_idx == 3)   # make Theme 3 the “glassy” theme by default


        # resize throttling state
        self._resize_job = None
        self._last_base_w = -1  # cache last computed width

        self._build_layout()
        self.apply_theme(theme_idx)

        self.root.bind("<Key>", self._on_key)

    # ---------- state ----------
    def _bind_state(self):
        self.attempts = 0
        self.current_guess = ""
        self.tried_words = []
        self.known_word = [None]*5
        self.present_letters = set()
        self.absent_letters = set()
        self.yellow_positions = set()

    def reset_solver_state(self, fresh=False):
        self._bind_state()
        if not fresh and hasattr(self, "tiles"):
            for r in range(self.max_attempts):
                for c in range(5):
                    self.tiles[r][c].configure(text="", fg_color=self.pal["grid_default"])
            for b in getattr(self, "key_buttons", {}).values():
                b.configure(state="normal")

    # ---------- theme ----------
    def apply_theme(self, idx: int):
        if getattr(self, "_current_theme", None) == idx:
            return
        self._current_theme = idx
        
        # root background: transparent for glass, solid otherwise
        self.theme_idx = idx
        self.pal = PALETTES[idx]

        self.glass = (idx == 3)

        if self.glass:
            # keep normal bg color; make window slightly translucent and enable acrylic
            try:
                self.root.attributes('-alpha', 0.92)
            except Exception:
                pass
            enable_glass(self.root, use_mica=False, alpha=160, tint_rgb=(70, 160, 200))
        else:
            try:
                self.root.attributes('-alpha', 1.0)
            except Exception:
                pass
            self.root.configure(fg_color=self.pal["bg"])



        self.root.configure(fg_color=self.pal["bg"])
        if hasattr(self, "board_card"):
            self.board_card.configure(fg_color=self.pal["card"])
        if hasattr(self, "kb_card"):
            self.kb_card.configure(fg_color=self.pal.get("kb_card", self.pal["card"]))

        if hasattr(self, "tiles"):
            for row in self.tiles:
                for t in row:
                    t.configure(fg_color=self.pal["grid_default"], text_color="#FFFFFF")

        if hasattr(self, "key_buttons"):
            for name, key in self.key_buttons.items():
                if hasattr(key, "set_colors"):
                    if name == "ENTER":
                        key.set_colors(bg=self.pal["equals"], fg=self.pal["equals_txt"], shadow=self.pal["rim"])
                    elif name in ("DEL", "BACK"):
                        key.set_colors(bg=self.pal["del"], fg="#ffffff", shadow=self.pal["rim"])
                    else:
                        key.set_colors(bg=self.pal["key"], fg=self.pal["key_txt"], shadow=self.pal["rim"])

        if hasattr(self, "rand_btn"):
            self.rand_btn.configure(fg_color=self.pal["op"], text_color="#ffffff")
        if hasattr(self, "submit_btn"):
            self.submit_btn.configure(fg_color=self.pal["reset"], text_color="#ffffff")
        if hasattr(self, "reset_btn"):
            self.reset_btn.configure(fg_color=self.pal["reset"], text_color="#ffffff")

        if hasattr(self, "theme_pills"):
            for i, pill in enumerate(self.theme_pills, start=1):
                pill.configure(fg_color=self.pal["equals"] if i == self.theme_idx else self.pal["key"])

    # ---------- layout ----------
    def _build_layout(self):
        self.root.title("Wordle Solver — Theme")
        
        if self.glass:
    # overall translucency (safe on CTk)
            try:
                self.root.attributes('-alpha', 0.92)   # 0.90–0.96 looks good
            except Exception:
                pass
            enable_glass(self.root, use_mica=False, alpha=170, tint_rgb=(26, 20, 40))
        else:
            try:
                self.root.attributes('-alpha', 1.0)
            except Exception:
                pass


        # Header
        header = ctk.CTkFrame(self.root, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 8))

        ctk.CTkLabel(header, text="Wordle Cheat", font=("Inter", 28, "bold")).pack(side="left")

        theme_box = ctk.CTkFrame(header, fg_color="transparent")
        theme_box.pack(side="right")

        ctk.CTkLabel(theme_box, text="THEME", font=self.FONT_SMALL).grid(row=0, column=0, padx=(0, 8))
        self.theme_pills = []
        for i in (1, 2, 3):
            b = ctk.CTkButton(theme_box, text=str(i), width=28, height=28,
                              corner_radius=14, fg_color="#333", hover_color="#333",
                              command=lambda k=i: self.apply_theme(k))
            b.grid(row=0, column=i, padx=4)
            self.theme_pills.append(b)

        # Board
        self.board_card = ctk.CTkFrame(self.root, corner_radius=18, height=300)
        self.board_card.pack(fill="x", padx=24, pady=(0, 16))

        grid = ctk.CTkFrame(self.board_card, fg_color="transparent")
        grid.pack(padx=12, pady=12)

        self.tiles = []
        for r in range(self.max_attempts):
            row = []
            for c in range(5):
                t = ctk.CTkLabel(grid, text="", width=64, height=64,
                                 corner_radius=12, fg_color="#222",
                                 font=self.FONT_LARGE, anchor="center")
                t.grid(row=r, column=c, padx=6, pady=6)
                row.append(t)
            self.tiles.append(row)

        # Keyboard
        self.kb_card = ctk.CTkFrame(self.root, corner_radius=18)
        self.kb_card.pack(fill="x", expand=False, padx=16, pady=(0, 12))

        kb = ctk.CTkFrame(self.kb_card, fg_color="transparent")
        kb.pack(padx=(4, 10), pady=12, anchor="w")   # tighter on left


        self.key_buttons = {}
        self._keys_in_order = []   # for faster iteration during resize
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for ridx, row in enumerate(rows):
            rr = ctk.CTkFrame(kb, fg_color="transparent")
            rr.grid(row=ridx, column=0, pady=6, sticky="w")

            start_col = 0


            for c, ch in enumerate(row):
                btn = ElevatedKey(
                    rr, text=ch,
                    bg=self.pal["key"], fg=self.pal["key_txt"],
                    shadow=self.pal["rim"], width=86, height=58,
                    command=lambda s=ch: self.enter_letter(s)
                )
                btn.grid(row=0, column=start_col + c, padx=10, pady=(0, 6), sticky="we")
                self.key_buttons[ch] = btn
                self._keys_in_order.append((ch, btn))

            if ridx == 2:
                col0 = start_col + len(row)

                enter = ElevatedKey(
                    rr, text="ENTER",
                    bg=self.pal["equals"], fg=self.pal["equals_txt"],
                    shadow=self.pal["rim"], width=120, height=58,
                    command=self.process_guess
                )
                enter.grid(row=0, column=col0, padx=10, pady=(0, 6), sticky="we")
                self.key_buttons["ENTER"] = enter
                self._keys_in_order.append(("ENTER", enter))

                back = ElevatedKey(
                    rr, text="DEL",
                    bg=self.pal["del"], fg="#ffffff",
                    shadow=self.pal["rim"], width=96, height=58,
                    command=self.backspace
                )
                back.grid(row=0, column=col0 + 1, padx=10, pady=(0, 6), sticky="we")
                self.key_buttons["DEL"] = back
                self._keys_in_order.append(("DEL", back))

        # Actions
        actions = ctk.CTkFrame(self.root, fg_color="transparent")
        actions.pack(pady=(0, 16))
        self.rand_btn   = ctk.CTkButton(actions, text="Random", corner_radius=14,
                                        width=110, hover=False, command=self.suggest_initial_word)
        self.rand_btn.pack(side="left", padx=6)
        self.submit_btn = ctk.CTkButton(actions, text="Submit", corner_radius=14,
                                        width=110, hover=False, state="disabled", command=self.process_guess)
        self.submit_btn.pack(side="left", padx=6)
        self.reset_btn  = ctk.CTkButton(actions, text="Reset", corner_radius=14,
                                        width=110, hover=False, command=self.reset_game)
        self.reset_btn.pack(side="left", padx=6)

        # Bind resize AFTER widgets exist (to kb_card only)
        self._bind_resize()

    # -------- responsive keyboard (debounced) ----------
    def _bind_resize(self):
        self.kb_card.bind("<Configure>", self._on_kb_configure)
        # initial pass
        self.root.after(20, self._resize_keys)

    def _on_kb_configure(self, _event):
        # debounce while resizing
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(80, self._resize_keys)

    def _resize_keys(self):
        self._resize_job = None
        kbw = self.kb_card.winfo_width()
        if kbw <= 1:
            return

        side_margin = 28
        gap = 16
        cols_top = 10

        base_w = (kbw - side_margin*2 - gap*(cols_top-1)) / cols_top
        base_w = max(48, min(96, int(base_w)))   # clamp

        # skip tiny changes to avoid thrashing
        if abs(base_w - self._last_base_w) < 1:
            return
        self._last_base_w = base_w

        key_h   = int(base_w * 0.68)
        shadow  = max(3, int(key_h * 0.12))
        font_sz = max(12, int(key_h * 0.38))

        for name, key in self._keys_in_order:
            if not hasattr(key, "set_size"):
                continue
            if name == "ENTER":
                w = int(base_w * 1.45)
            elif name in ("DEL", "BACK"):
                w = int(base_w * 1.15)
            else:
                w = int(base_w)
            key.set_size(w, key_h, offset=(0, shadow), font_size=font_sz)

    # ---------- input ----------
    def _on_key(self, e):
        ch = e.char.upper()
        if ch.isalpha() and len(ch) == 1:
            self.enter_letter(ch)
        elif e.keysym == "BackSpace":
            self.backspace()
        elif e.keysym == "Return":
            if len(self.current_guess) == 5:
                self.process_guess()

    def enter_letter(self, letter):
        if len(self.current_guess) < 5 and letter.isalpha():
            self.current_guess += letter
            self._refresh_current_guess()
            self.submit_btn.configure(state="normal" if len(self.current_guess) == 5 else "disabled")

    def backspace(self):
        if self.current_guess:
            self.current_guess = self.current_guess[:-1]
            self._refresh_current_guess()
            if len(self.current_guess) < 5:
                self.submit_btn.configure(state="disabled")

    def _refresh_current_guess(self):
        for i in range(5):
            ch = self.current_guess[i] if i < len(self.current_guess) else ""
            self.tiles[self.attempts][i].configure(text=ch)

    # ---------- actions ----------
    def suggest_initial_word(self):
        if not self.words: return
        w = random.choice(self.words)
        messagebox.showinfo("Initial Word", f"Try starting with: {w}")
        self.current_guess = w
        self._refresh_current_guess()
        self.submit_btn.configure(state="normal")

    def process_guess(self):
        if len(self.current_guess) != 5: return
        guess = self.current_guess.upper()
        self.get_feedback(guess)

    # ---------- feedback ----------
    def get_feedback(self, guess):
        dlg = ctk.CTkToplevel(self.root)
        dlg.title(f"Feedback: {guess}")
        dlg.grab_set()
        frm = ctk.CTkFrame(dlg)
        frm.pack(padx=16, pady=16)

        colors = [self.pal["grid_default"]]*5
        chips  = []

        def apply_color(i, kind):
            col = {"G":self.pal["grid_correct"], "Y":self.pal["grid_present"], "X":self.pal["grid_absent"]}[kind]
            colors[i] = col
            chips[i].configure(fg_color=col)

        for i, ch in enumerate(guess):
            row = ctk.CTkFrame(frm, fg_color="transparent")
            row.pack(pady=6, fill="x")

            ctk.CTkLabel(row, text=ch, width=30).pack(side="left")
            ctk.CTkButton(row, text="Green",  width=72, hover=False,
                          command=lambda k=i: apply_color(k, "G")).pack(side="left", padx=4)
            ctk.CTkButton(row, text="Yellow", width=72, hover=False,
                          command=lambda k=i: apply_color(k, "Y")).pack(side="left", padx=4)
            ctk.CTkButton(row, text="Gray",   width=72, hover=False,
                          command=lambda k=i: apply_color(k, "X")).pack(side="left", padx=4)

            chip = ctk.CTkLabel(row, text="  ", width=36, height=28, corner_radius=8,
                                fg_color=self.pal["grid_default"])
            chip.pack(side="right", padx=6)
            chips.append(chip)

        def commit():
            for i, col in enumerate(colors):
                tile = self.tiles[self.attempts][i]
                tile.configure(text=guess[i], fg_color=col)

                if col == self.pal["grid_correct"]:
                    self.known_word[i] = guess[i]
                    self.present_letters.add(guess[i])
                elif col == self.pal["grid_present"]:
                    self.present_letters.add(guess[i])
                    self.yellow_positions.add((guess[i], i))
                elif col == self.pal["grid_absent"]:
                    if guess[i] not in self.known_word and guess[i] not in self.present_letters:
                        self.absent_letters.add(guess[i])
                        if guess[i] in self.key_buttons:
                            self.key_buttons[guess[i]].configure(state="disabled")

            if all(c == self.pal["grid_correct"] for c in colors):
                dlg.destroy()
                self.show_victory(guess)
                return

            self.tried_words.append(guess)
            self.attempts += 1
            dlg.destroy()
            self.current_guess = ""
            self._refresh_current_guess()
            self.submit_btn.configure(state="disabled")

            if self.attempts >= self.max_attempts:
                messagebox.showinfo("Game Over", "Out of attempts.")
                self.reset_game()
            else:
                self.suggest_next_word()

        ctk.CTkButton(frm, text="Apply Feedback", hover=False, command=commit).pack(pady=10)

    # ---------- solver core ----------
    def filter_words(self):
        return filter_words(
            self.words, set(self.tried_words), self.known_word,
            self.absent_letters, self.present_letters, self.yellow_positions
        )

    def suggest_next_word(self):
        cand = self.filter_words()
        if cand:
            nxt = random.choice(cand)
            messagebox.showinfo("Next Guess", f"Try: {nxt}")
            self.current_guess = nxt
            self._refresh_current_guess()
            self.submit_btn.configure(state="normal")
        else:
            messagebox.showinfo("Info", "No matching words remain with current feedback.")

    # ---------- victory / reset ----------
    def show_victory(self, word):
        today = datetime.date.today().strftime("%Y-%m-%d")
        try:
            with open("complete.txt", "a", encoding="utf-8") as f:
                f.write(f"{today} : {word}\n")
        except Exception as e:
            print("Could not write to complete.txt:", e)

        win = ctk.CTkToplevel(self.root)
        win.title("🎉 Victory!")
        ctk.CTkLabel(win, text=f"Congratulations!\nYou found: {word}",
                     font=("Inter", 22, "bold")).pack(padx=24, pady=20)
        ctk.CTkButton(win, text="Play Again", hover=False,
                      command=lambda: [win.destroy(), self.reset_game()]).pack(pady=6)
        ctk.CTkButton(win, text="Exit", hover=False,
                      command=self.root.destroy).pack(pady=6)

    def reset_game(self):
        self.reset_solver_state(fresh=False)
