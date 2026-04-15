import customtkinter as ctk

# =========================================================
# THEME CHUNG TOÀN APP
# =========================================================

class Theme:
    BG = "#F4F6FB"
    CARD = "#FFFFFF"

    PRIMARY = "#1565C0"
    PRIMARY_HOVER = "#0D47A1"

    SUCCESS = "#2E7D32"
    WARNING = "#F9A825"
    DANGER = "#C62828"

    TEXT = "#111827"
    TEXT_GRAY = "#6B7280"

    BORDER = "#E5E7EB"


class Font:
    TITLE = ctk.CTkFont(size=22, weight="bold")
    HEADER = ctk.CTkFont(size=16, weight="bold")
    NORMAL = ctk.CTkFont(size=13)
    SMALL = ctk.CTkFont(size=11)


def apply_theme(root):
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root.configure(fg_color=Theme.BG)


def card(parent):
    return ctk.CTkFrame(
        parent,
        fg_color=Theme.CARD,
        corner_radius=14,
        border_width=1,
        border_color=Theme.BORDER
    )


def primary_btn(parent, **kw):
    return ctk.CTkButton(
        parent,
        fg_color=Theme.PRIMARY,
        hover_color=Theme.PRIMARY_HOVER,
        height=36,
        corner_radius=10,
        font=Font.NORMAL,
        **kw
    )


def danger_btn(parent, **kw):
    return ctk.CTkButton(
        parent,
        fg_color=Theme.DANGER,
        hover_color="#B71C1C",
        height=36,
        corner_radius=10,
        font=Font.NORMAL,
        **kw
    )


def entry(parent, **kw):
    return ctk.CTkEntry(
        parent,
        height=36,
        corner_radius=10,
        font=Font.NORMAL,
        **kw
    )