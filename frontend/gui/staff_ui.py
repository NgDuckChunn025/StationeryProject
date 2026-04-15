import customtkinter as ctk
from tkinter import ttk, messagebox
from backend.modules import staff_service as svc

style = ttk.Style()
style.theme_use("default")

style.configure(
    "Treeview",
    font=("Segoe UI", 12),
    rowheight=32
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 13, "bold")
)

class StaffFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()
        self._load()

    def _build(self):
        ctk.CTkLabel(self, text="QUẢN LÝ NHÂN VIÊN",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=10)

        # TABLE
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Tên", "Tài khoản", "Vai trò")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=200)

        self.tree.pack(fill="both", expand=True)

        # BUTTON
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(btn_frame, text="Thêm",
                      command=self._add).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="Xóa",
                      fg_color="#C62828",
                      command=self._delete).pack(side="right", padx=5)

    def _load(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        for r in svc.get_all():
            self.tree.insert("", "end", iid=r[0], values=(r[1], r[2], r[3]))

    def _add(self):
        StaffDialog(self, self._load)

    def _delete(self):
        sel = self.tree.selection()
        if sel:
            svc.delete(int(sel[0]))
            self._load()


# ================= DIALOG =================
class StaffDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback

        self.geometry("400x350")
        self.title("Thêm nhân viên")

        frm = ctk.CTkFrame(self, fg_color="transparent")
        frm.pack(fill="both", expand=True, padx=30, pady=20)

        self.e_name = ctk.CTkEntry(frm, placeholder_text="Tên nhân viên", height=38)
        self.e_name.pack(fill="x", pady=6)

        self.e_user = ctk.CTkEntry(frm, placeholder_text="Tài khoản", height=38)
        self.e_user.pack(fill="x", pady=6)

        self.e_pass = ctk.CTkEntry(frm, placeholder_text="Mật khẩu", height=38)
        self.e_pass.pack(fill="x", pady=6)

        self.cmb = ctk.CTkComboBox(frm, values=["admin", "staff"], height=38)
        self.cmb.pack(fill="x", pady=6)

        ctk.CTkButton(frm, text="Lưu",
                      height=40,
                      fg_color="#2E7D32",
                      command=self._save).pack(fill="x", pady=10)

    def _save(self):
        ok, msg = svc.add(
            self.e_name.get(),
            self.e_user.get(),
            self.e_pass.get(),
            self.cmb.get()
        )

        (messagebox.showinfo if ok else messagebox.showerror)("KQ", msg)

        if ok:
            self.callback()
            self.destroy()