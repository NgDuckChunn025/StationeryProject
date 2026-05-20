# frontend/gui/theme.py — Design System v3 (chuyên nghiệp)
import customtkinter as ctk
from tkinter import ttk
FONT = "Segoe UI"
FONT_BOLD = "Segoe UI Semibold"

PRIMARY       = "#2563EB"
PRIMARY_DARK  = "#1D4ED8"
PRIMARY_LIGHT = "#DBEAFE"
PRIMARY_HOVER = "#1E40AF"

SUCCESS       = "#16A34A"
SUCCESS_DARK  = "#15803D"
SUCCESS_LIGHT = "#DCFCE7"

WARNING       = "#EA580C"
WARNING_DARK  = "#C2410C"
WARNING_LIGHT = "#FFEDD5"

DANGER        = "#DC2626"
DANGER_DARK   = "#B91C1C"
DANGER_LIGHT  = "#FEE2E2"

PURPLE        = "#7C3AED"
PURPLE_DARK   = "#6D28D9"
PURPLE_LIGHT  = "#F3E8FF"

TEAL          = "#0891B2"
TEAL_LIGHT    = "#CFFAFE"

BG     = "#F8FAFC"
CARD   = "#FFFFFF"
BORDER = "#D8E2EE"
BORDER2= "#B8CEE8"

TEXT_PRIMARY = "#1C2535"
TEXT_SECOND  = "#3E5068"
TEXT_GRAY    = "#6B7E96"
TEXT_WHITE   = "#FFFFFF"

SP_XS = 4;  SP_SM = 8;  SP_MD = 16;  SP_LG = 20;  SP_XL = 28
FS_XS=10
FS_SM=12
FS_BASE=13
FS_MD=14
FS_LG=16
FS_XL=20
FS_2XL=24
BTN_SM=30; BTN_MD=36; BTN_LG=42
RADIUS_SM=6; RADIUS_MD=8; RADIUS_LG=12


def apply_treeview_style(style_obj, name="VPP.Treeview"):
    style_obj.theme_use("clam")
    style_obj.configure(name,
        background="#FFFFFF", foreground=TEXT_PRIMARY,
        rowheight=36, fieldbackground="#FFFFFF",
        font=("Segoe UI", FS_BASE), borderwidth=0, relief="flat")
    style_obj.configure(f"{name}.Heading",
        font=("Segoe UI", FS_BASE, "bold"),
        background=PRIMARY, foreground="#FFFFFF",
        relief="flat", borderwidth=0, padding=(8, 8))
    style_obj.map(name,
        background=[("selected", "#D0E8FF")],
        foreground=[("selected", PRIMARY_DARK)])
    style_obj.configure("VPP.Vertical.TScrollbar",
        troughcolor="#EEF2F7", background="#BBCAD8",
        arrowcolor=TEXT_GRAY, borderwidth=0, relief="flat", width=7)
    style_obj.map("VPP.Vertical.TScrollbar",
        background=[("active", PRIMARY_LIGHT)])
    return name


def make_btn(parent, text, command=None, style="primary",
             width=None, height=BTN_MD, icon=""):
    palettes = {
        "primary": (PRIMARY,      PRIMARY_DARK,  TEXT_WHITE),
        "success": (SUCCESS,      SUCCESS_DARK,  TEXT_WHITE),
        "warning": (WARNING,      WARNING_DARK,  TEXT_WHITE),
        "danger":  (DANGER,       DANGER_DARK,   TEXT_WHITE),
        "ghost":   (PRIMARY_LIGHT,"#BBDEFB",     PRIMARY),
        "purple":  (PURPLE,       PURPLE_DARK,   TEXT_WHITE),
        "teal":    (TEAL,         "#0C4A6E",     TEXT_WHITE),
        "neutral": ("#5A6A7E",    "#3E4F61",     TEXT_WHITE),
    }
    fg, hover, tc = palettes.get(style, palettes["primary"])
    label = f"{icon}  {text}" if icon else text
    kw = dict(text=label, height=height,
              font=ctk.CTkFont(size=FS_BASE, weight="bold"),
              fg_color=fg, hover_color=PRIMARY_HOVER, text_color=tc,
              corner_radius=RADIUS_MD, command=command, cursor="hand2")
    if width: kw["width"] = width
    return ctk.CTkButton(parent, **kw)


def page_header(parent, title: str, subtitle: str = ""):
    frm = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(frm, text=title,
                 font=ctk.CTkFont(
                     family=FONT_BOLD,
                     size=28,
                     weight="bold"
                 ),
                 text_color=TEXT_PRIMARY).pack(anchor="w")
    if subtitle:
        ctk.CTkLabel(frm, text=subtitle,
                     font=ctk.CTkFont(size=FS_SM),
                     text_color=TEXT_GRAY).pack(anchor="w", pady=(1,0))
    return frm


def make_card(parent, **kw):
    d = dict(fg_color=CARD, corner_radius=RADIUS_LG,
             border_width=1, border_color=BORDER)
    d.update(kw)
    return ctk.CTkFrame(parent, **d)


def divider(parent):
    return ctk.CTkFrame(parent, fg_color=BORDER, height=1)


def section_label(parent, text: str):
    return ctk.CTkLabel(parent, text=text, anchor="w",
                        font=ctk.CTkFont(size=FS_SM, weight="bold"),
                        text_color=TEXT_SECOND)


def badge(parent, text: str, color: str = PRIMARY):
    """Mini badge label."""
    f = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
    ctk.CTkLabel(f, text=text,
                 font=ctk.CTkFont(size=FS_XS, weight="bold"),
                 text_color="white").pack(padx=8, pady=2)
    return f
