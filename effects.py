# effects.py — Windows acrylic / mica helpers (safe no-ops on other OSes)
import sys
import ctypes
from ctypes import wintypes

# ---- Windows structs/constants
class _ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_uint32),  # AARRGGBB
        ("AnimationId", ctypes.c_int),
    ]

class _WCA_DATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.c_void_p),
        ("SizeOfData", ctypes.c_size_t),
    ]

_WCA_ACCENT_POLICY = 19
_ACCENT_ENABLE_BLURBEHIND = 3
_ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

def _apply_acrylic_hwnd(hwnd, alpha, tint_rgb):
    a, (r, g, b) = alpha, tint_rgb
    gradient = (a << 24) | (r << 16) | (g << 8) | b

    policy = _ACCENT_POLICY()
    policy.AccentState = _ACCENT_ENABLE_ACRYLICBLURBEHIND
    policy.AccentFlags = 0x20 | 0x40 | 0x80  # safe defaults
    policy.GradientColor = gradient
    policy.AnimationId = 0

    data = _WCA_DATA()
    data.Attribute = _WCA_ACCENT_POLICY
    # Chun : c_void_p needs an actual void*, so cast the struct pointer explicitly
    data.Data = ctypes.cast(ctypes.byref(policy), ctypes.c_void_p)
    data.SizeOfData = ctypes.sizeof(policy)

    SetWCA = ctypes.windll.user32.SetWindowCompositionAttribute
    # Chun : teach ctypes the signature so it stops guessing
    SetWCA.argtypes = [wintypes.HWND, ctypes.POINTER(_WCA_DATA)]
    SetWCA.restype = wintypes.BOOL

    ok = SetWCA(wintypes.HWND(hwnd), ctypes.byref(data))
    if not ok:
        policy.AccentState = _ACCENT_ENABLE_BLURBEHIND
        SetWCA(wintypes.HWND(hwnd), ctypes.byref(data))

def _apply_mica_hwnd(hwnd):
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMSBT_MAINWINDOW = 2
    val = ctypes.c_int(1)
    mica = ctypes.c_int(DWMSBT_MAINWINDOW)
    DwmSet = ctypes.windll.dwmapi.DwmSetWindowAttribute
    DwmSet(wintypes.HWND(hwnd), ctypes.c_int(DWMWA_USE_IMMERSIVE_DARK_MODE),
           ctypes.byref(val), ctypes.sizeof(val))
    DwmSet(wintypes.HWND(hwnd), ctypes.c_int(DWMWA_SYSTEMBACKDROP_TYPE),
           ctypes.byref(mica), ctypes.sizeof(mica))

def enable_glass(root, *, use_mica=False, alpha=170, tint_rgb=(26, 20, 40)):
    """
    Enable OS blur behind the Tk/CTk root window.
    - use_mica: Windows 11 Mica instead of Acrylic
    - alpha: 0..255 (lower is more glassy)
    - tint_rgb: (r,g,b) tint to match your theme
    Safe no-op on non-Windows.
    """
    if not sys.platform.startswith("win"):
        return
    try:
        hwnd = root.winfo_id()
        if use_mica:
            _apply_mica_hwnd(hwnd)
        else:
            _apply_acrylic_hwnd(hwnd, alpha, tint_rgb)
    except Exception as e:
        # Chun : if we can't get hwnd or apply effects, just skip gracefully
        print("Glass effect unavailable:", e)
