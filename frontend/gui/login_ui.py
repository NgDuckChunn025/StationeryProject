# frontend/gui/login_ui.py
import customtkinter as ctk
from tkinter import messagebox
from frontend.gui.theme import (
    PRIMARY, PRIMARY_DARK, PRIMARY_LIGHT,
    CARD, BORDER, BG,
    TEXT_PRIMARY, TEXT_SECOND, TEXT_GRAY,
    FS_XS, FS_SM, FS_MD, FS_LG, FS_2XL,
    BTN_MD, BTN_LG, RADIUS_MD, RADIUS_SM,
    SP_SM, SP_MD, SP_LG,
)
from backend.modules.auth_service import login


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VPP Manager — Đăng nhập")
        self.geometry("420x560")
        self.resizable(False, False)
        self.eval("tk::PlaceWindow . center")
        self.configure(fg_color=BG)
        self.user_info = None
        self._build()

    def _build(self):
        # ── Blue header ───────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=PRIMARY,
                            corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="🛒",
                     font=ctk.CTkFont(size=40)).pack(pady=(28, 4))
        ctk.CTkLabel(hdr, text="VPP Manager",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="white").pack()
        ctk.CTkLabel(hdr,
                     text="Phần mềm quản lý cửa hàng văn phòng phẩm",
                     font=ctk.CTkFont(size=FS_SM),
                     text_color="#A8CFEF").pack(pady=(2, 24))

        # ── Form card ─────────────────────────────────────────
        card = ctk.CTkFrame(self, fg_color=CARD,
                             corner_radius=12,
                             border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=36, pady=24)

        inner = ctk.CTkFrame(card, fg_color=CARD)
        inner.pack(fill="x", padx=SP_LG, pady=SP_LG)

        def lbl(text):
            ctk.CTkLabel(inner, text=text, anchor="w",
                         font=ctk.CTkFont(size=FS_SM, weight="bold"),
                         text_color=TEXT_SECOND
                         ).pack(fill="x", pady=(SP_SM, 2))

        lbl("Tài khoản")
        self.ent_user = ctk.CTkEntry(
            inner, height=BTN_LG,
            font=ctk.CTkFont(size=FS_MD),
            placeholder_text="Nhập tài khoản...",
            fg_color=CARD, border_color=BORDER,
            corner_radius=RADIUS_SM)
        self.ent_user.pack(fill="x")
        self.ent_user.insert(0, "admin")

        lbl("Mật khẩu")
        self.ent_pass = ctk.CTkEntry(
            inner, height=BTN_LG, show="•",
            font=ctk.CTkFont(size=FS_MD),
            placeholder_text="Nhập mật khẩu...",
            fg_color=CARD, border_color=BORDER,
            corner_radius=RADIUS_SM)
        self.ent_pass.pack(fill="x")
        self.ent_pass.insert(0, "123456")


        # Nút đăng nhập
        self.btn = ctk.CTkButton(
            inner, text="ĐĂNG NHẬP", height=BTN_LG,
            font=ctk.CTkFont(size=FS_MD, weight="bold"),
            fg_color=PRIMARY, hover_color=PRIMARY_DARK,
            corner_radius=RADIUS_MD, cursor="hand2",
            command=self._do_login)
        self.btn.pack(fill="x", pady=(SP_MD, 0))

        self.ent_pass.bind("<Return>", lambda _: self._do_login())
        self.ent_user.bind("<Return>",
                           lambda _: self.ent_pass.focus())

    def _do_login(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Thiếu thông tin",
                                   "Vui lòng nhập tài khoản và mật khẩu!")
            return
        self.btn.configure(text="Đang kiểm tra...",
                           state="disabled")
        self.update()
        result = login(u, p)
        if result:
            self.user_info = result
            self.destroy()
        else:
            messagebox.showerror("Sai thông tin",
                                  "Tài khoản hoặc mật khẩu không đúng!")
            self.btn.configure(text="ĐĂNG NHẬP", state="normal")
            self.ent_pass.delete(0, "end")
            self.ent_pass.focus()
