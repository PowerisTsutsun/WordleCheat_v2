# utils.py
import os, sys
import customtkinter as ctk

def resource_path(rel_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):  # PyInstaller support
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

def init_ctk(mode="dark"):
    # Chun : theme defaults here are a sensible base; palettes will style specifics
    ctk.set_appearance_mode(mode)  # "dark", "light", or "system"
    ctk.set_default_color_theme("dark-blue")
    ctk.set_widget_scaling(1.0)   # 1.0–1.25 typical
    ctk.set_window_scaling(1.0)

