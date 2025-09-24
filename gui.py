# gui.py
import sys
from effects import enable_glass
from collections import Counter  # Chun : using this for duplicate-letter feedback accounting
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
        self.words = words  # Chun : already uppercased in app.py for consistency
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
        self.exact_counts = {}     # Chun : track exact duplicate counts when feedback indicates it
        self.feedback_mode = False # Chun : toggles when user is marking tile feedback

    def reset_solver_state(self, fresh=False):
        self._bind_state()
        if not fresh and hasattr(self, "tiles"):
            for r in range(self.max_attempts):
                for c in range(5):
                    self.tiles[r][c].configure(text="", fg_color=self.pal["grid_default"])
            for b in getattr(self, "key_buttons", {}).values():
                b.configure(state="normal")
            if hasattr(self, "status_label"):
                self.status_label.configure(text="")  # Chun : clear status on reset

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
            # Chun : set bg once below; avoid duplicate configure here



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
        if hasattr(self, "reset_btn"):
            self.reset_btn.configure(fg_color=self.pal["reset"], text_color="#ffffff")

        if hasattr(self, "theme_pills"):
            for i, pill in enumerate(self.theme_pills, start=1):
                pill.configure(fg_color=self.pal["equals"] if i == self.theme_idx else self.pal["key"])
        if hasattr(self, "status_label"):
            self.status_label.configure(text_color=self.pal["text"])  # Chun : keep status text readable per theme

    # ---------- layout ----------
    def _build_layout(self):
        self.root.title("Wordle Cheat")  # Chun : rename to match app vibe
        
        # Chun : glass/acrylic setup is handled in apply_theme() to avoid duplication here


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

        # Chun : make the board responsive so tiles scale nicely
        self.board_card.grid_propagate(False)
        self.board_card.grid_columnconfigure(0, weight=1)
        self.board_card.grid_rowconfigure(0, weight=1)

        grid = ctk.CTkFrame(self.board_card, fg_color="transparent")
        grid.pack(padx=12, pady=12)

        self.tiles = []
        for r in range(self.max_attempts):
            row = []
            for c in range(5):
                grid.grid_columnconfigure(c, weight=1)
                grid.grid_rowconfigure(r, weight=1)
                t = ctk.CTkLabel(grid, text="", corner_radius=12,
                                 fg_color="#222", font=self.FONT_LARGE,
                                 anchor="center")
                t.grid(row=r, column=c, padx=6, pady=6)
                row.append(t)
                t.bind("<Button-1>", lambda e, r=r, c=c: self._on_tile_clicked(r, c))  # Chun : click to set feedback
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
                    command=self.handle_enter_key  # Chun : ENTER toggles between marking and confirming feedback
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
        self.rand_btn.pack(side="left", padx=8)
        self.reset_btn  = ctk.CTkButton(actions, text="Reset", corner_radius=14,
                                        width=110, hover=False, command=self.reset_game)
        self.reset_btn.pack(side="left", padx=8)

        # Chun : inline status so users don't get spammed with popups
        self.status_label = ctk.CTkLabel(self.root, text="", font=self.FONT_SMALL)
        self.status_label.pack(pady=(0, 10), fill="x", padx=24)

        # Bind resize AFTER widgets exist (to kb_card only)
        self._bind_resize()

    # -------- responsive keyboard (debounced) ----------
    def _bind_resize(self):
        # Keyboard
        self.kb_card.bind("<Configure>", self._on_kb_configure)
        # initial pass
        self.root.after(20, self._resize_keys)
        # Board
        self.board_card.bind("<Configure>", self._on_board_configure)
        self.root.after(20, self._resize_board_tiles)  # Chun : kick a first resize so tiles look right

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

    def _on_board_configure(self, _event):
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(80, self._resize_board_tiles)

    def _resize_board_tiles(self):
        self._resize_job = None
        w = self.board_card.winfo_width()
        h = self.board_card.winfo_height()
        if w <= 1 or h <= 1:
            return

        # Chun : compute tile size based on available width/height
        gap = 12
        tile_w = (w - gap * 6) / 5
        tile_h = (h - gap * 7) / 6
        size = int(min(tile_w, tile_h))
        size = max(32, size)  # clamp to sensible min

        font_size = max(16, int(size * 0.5))
        font = ("Inter", font_size, "bold")
        radius = max(8, int(size * 0.15))

        for row in self.tiles:
            for tile in row:
                tile.configure(width=size, height=size, font=font, corner_radius=radius)

    # ---------- input ----------
    def _on_key(self, e):
        # Chun : still allow Enter to confirm while in feedback mode
        if e.keysym == "Return":
            self.handle_enter_key()
            return
        if self.feedback_mode:
            return  # Chun : ignore other typing while setting feedback on tiles
        ch = e.char.upper()
        if ch.isalpha() and len(ch) == 1:
            self.enter_letter(ch)
        elif e.keysym == "BackSpace":
            self.backspace()

    def enter_letter(self, letter):
        if len(self.current_guess) < 5 and letter.isalpha():
            self.current_guess += letter
            self._refresh_current_guess()

    def backspace(self):
        if self.current_guess:
            self.current_guess = self.current_guess[:-1]
            self._refresh_current_guess()

    def _refresh_current_guess(self):
        for i in range(5):
            ch = self.current_guess[i] if i < len(self.current_guess) else ""
            self.tiles[self.attempts][i].configure(text=ch)

    # ---------- actions ----------
    def suggest_initial_word(self):
        if not self.words: return
        w = random.choice(self.words)
        # Chun : no modal popup; surface the suggestion inline
        self.current_guess = w
        self._refresh_current_guess()
        if hasattr(self, "status_label"):
            self.status_label.configure(text=f"Starting suggestion: {w}")

    def handle_enter_key(self):
        # Chun : ENTER switches modes. If we're marking feedback, confirm it; otherwise enter feedback mode.
        if self.feedback_mode:
            self.commit_feedback()
        elif len(self.current_guess) == 5:
            self.enter_feedback_mode()

    def enter_feedback_mode(self):
        if len(self.current_guess) != 5:
            return
        self.feedback_mode = True
        # Chun : prefill current row as all GREY so cycling is predictable
        for i in range(5):
            ch = self.current_guess[i]
            tile = self.tiles[self.attempts][i]
            tile.configure(text=ch, fg_color=self.pal["grid_absent"])  # start at grey
        # flip ENTER to a confirm button so it's obvious
        if "ENTER" in self.key_buttons and hasattr(self.key_buttons["ENTER"], "_btn"):
            self.key_buttons["ENTER"]._btn.configure(text="CONFIRM")
        if hasattr(self, "status_label"):
            self.status_label.configure(text="Click each tile to set Grey/Yellow/Green, then press CONFIRM.")

    # ---------- feedback ----------
    def _on_tile_clicked(self, r, c):
        if not self.feedback_mode or r != self.attempts:
            return

        tile = self.tiles[r][c]
        current_color = tile.cget("fg_color")

        # Chun : cycle Grey -> Yellow -> Green on each click for a simple UX
        color_cycle = [
            self.pal["grid_absent"],
            self.pal["grid_present"],
            self.pal["grid_correct"],
        ]

        try:
            idx = color_cycle.index(current_color)
            next_color = color_cycle[(idx + 1) % len(color_cycle)]
        except ValueError:
            next_color = color_cycle[0]

        tile.configure(fg_color=next_color)

    def commit_feedback(self):
        guess = self.current_guess
        colors = [self.tiles[self.attempts][i].cget("fg_color") for i in range(5)]

        # Chun : capture duplicate info — if a letter got any non-grey, we know how many occurrences are real
        guess_counts = Counter(guess)
        feedback_counts = Counter()
        for i, ch in enumerate(guess):
            if colors[i] != self.pal["grid_absent"]:
                feedback_counts[ch] += 1

        for ch, total_count in guess_counts.items():
            colored_count = feedback_counts[ch]
            if 0 < colored_count < total_count:
                self.exact_counts[ch] = colored_count

        for i, col in enumerate(colors):
            char = guess[i]
            if col == self.pal["grid_correct"]:
                self.known_word[i] = char
                self.present_letters.add(char)
                if (char, i) in self.yellow_positions:
                    self.yellow_positions.remove((char, i))  # Chun : no longer just yellow here
            elif col == self.pal["grid_present"]:
                self.present_letters.add(char)
                self.yellow_positions.add((char, i))
            elif col == self.pal["grid_absent"]:
                if char not in self.present_letters and feedback_counts[char] == 0:
                    self.absent_letters.add(char)
                    if char in self.key_buttons:
                        self.key_buttons[char].configure(state="disabled")

        if all(c == self.pal["grid_correct"] for c in colors):
            self.show_victory(guess)
            return

        self.tried_words.append(guess)
        self.attempts += 1
        self.current_guess = ""
        self.feedback_mode = False
        if "ENTER" in self.key_buttons and hasattr(self.key_buttons["ENTER"], "_btn"):
            self.key_buttons["ENTER"]._btn.configure(text="ENTER")
        if hasattr(self, "status_label"):
            self.status_label.configure(text="")

        if self.attempts >= self.max_attempts:
            messagebox.showinfo("Game Over", "Out of attempts.")
            self.reset_game()
        else:
            self.suggest_next_word()

    # ---------- solver core ----------
    def filter_words(self):
        return filter_words(
            self.words, set(self.tried_words), self.known_word,
            self.absent_letters, self.present_letters, self.yellow_positions,
            self.exact_counts
        )

    def suggest_next_word(self):
        cand = self.filter_words()
        if cand:
            nxt = random.choice(cand)
            # Chun : surface suggestion inline (and show remaining count)
            if hasattr(self, "status_label"):
                self.status_label.configure(text=f"Suggestion: {nxt} ({len(cand)} words remain)")
            self.current_guess = nxt
            self._refresh_current_guess()
        else:
            if hasattr(self, "status_label"):
                self.status_label.configure(text="No matching words remain with current feedback.")

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
