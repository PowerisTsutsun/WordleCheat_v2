# widgets.py
import customtkinter as ctk

class ElevatedKey(ctk.CTkFrame):
    """Raised key with a soft shadow; supports dynamic resizing."""

    def __init__(self, parent, *,
                 text, bg, fg, shadow,
                 width=76, height=58, radius=16,
                 offset=(0, 6), font=("Inter", 20, "bold"),
                 command=None):
        super().__init__(parent, fg_color="transparent", width=width, height=height)

        self._cmd = command
        self._radius = radius
        self._font_family = font[0]

        self._shadow = ctk.CTkFrame(self, fg_color=shadow, corner_radius=radius,
                                    width=width, height=height)
        self._btn = ctk.CTkButton(
            self, text=text, fg_color=bg, text_color=fg,
            hover=False,  # smoother
            corner_radius=radius, font=font, width=width, height=height,
            command=self._on_click
        )

        sx, sy = offset
        self._shadow.place(x=sx, y=sy)
        self._btn.place(x=0, y=0)

        self.grid_propagate(False)
        self.pack_propagate(False)

    def _on_click(self):
        if self._cmd:
            self._cmd()

    def set_colors(self, *, bg=None, fg=None, shadow=None):
        if bg is not None:
            self._btn.configure(fg_color=bg)
        if fg is not None:
            self._btn.configure(text_color=fg)
        if shadow is not None:
            self._shadow.configure(fg_color=shadow)

    def set_size(self, width: int, height: int, *, offset=None, font_size=None):
        """Resize key + shadow; optionally adjust shadow offset and font size."""
        self.configure(width=width, height=height)
        cr = int(height * 0.28)
        self._btn.configure(width=width, height=height, corner_radius=cr)
        self._shadow.configure(width=width, height=height, corner_radius=cr)
        if offset is not None:
            sx, sy = offset
            self._shadow.place_configure(x=sx, y=sy)
        if font_size is not None:
            self._btn.configure(font=(self._font_family, int(font_size), "bold"))

    # forward state to inner CTkButton
    def configure(self, **kw):
        if "state" in kw:
            self._btn.configure(state=kw.pop("state"))
        return super().configure(**kw)
