# frontend/gui/login_ui.py
# ================================================================
# Màn hình đăng nhập
# ================================================================

import customtkinter as ctk
from tkinter import messagebox
from backend.modules.auth_service import login


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Đăng nhập — VPP Manager")
        self.geometry("420x520")
        self.resizable(False, False)
        self.eval("tk::PlaceWindow . center")
        self.user_info = None
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="#1565C0", corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="  VPP Manager",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color="white").pack(pady=(30, 6))
        ctk.CTkLabel(hdr, text="Phần mềm quản lý cửa hàng văn phòng phẩm",
                     font=ctk.CTkFont(size=12),
                     text_color="#BBDEFB").pack(pady=(0, 24))

        # Form
        frm = ctk.CTkFrame(self, fg_color="transparent")
        frm.pack(fill="both", expand=True, padx=40, pady=28)

        ctk.CTkLabel(frm, text="Tài khoản", anchor="w",
                     font=ctk.CTkFont(size=13)).pack(fill="x", pady=(0, 4))
        self.ent_user = ctk.CTkEntry(frm, height=40, font=ctk.CTkFont(size=13),
                                      placeholder_text="Nhập tài khoản...")
        self.ent_user.pack(fill="x")
        self.ent_user.insert(0, "admin")

        ctk.CTkLabel(frm, text="Mật khẩu", anchor="w",
                     font=ctk.CTkFont(size=13)).pack(fill="x", pady=(14, 4))
        self.ent_pass = ctk.CTkEntry(frm, height=40, show="*",
                                      font=ctk.CTkFont(size=13),
                                      placeholder_text="Nhập mật khẩu...")
        self.ent_pass.pack(fill="x")
        self.ent_pass.insert(0, "123456")

        self.btn = ctk.CTkButton(
            frm, text="ĐĂNG NHẬP", height=46,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1565C0", hover_color="#0D47A1",
            command=self._do_login
        )
        self.btn.pack(fill="x", pady=(26, 0))

        ctk.CTkLabel(frm, text=" ",
                     text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=10)

        self.ent_pass.bind("<Return>", lambda _: self._do_login())
        self.ent_user.bind("<Return>", lambda _: self.ent_pass.focus())

    def _do_login(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Thiếu thông tin",
                                   "Vui lòng nhập tài khoản và mật khẩu!")
            return
        self.btn.configure(text="Đang kiểm tra...", state="disabled")
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