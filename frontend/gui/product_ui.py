import customtkinter as ctk
from tkinter import ttk, messagebox
from backend.modules import product_service as svc


# ===== STYLE TABLE =====
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="white",
    foreground="#1F2937",
    rowheight=38,
    font=("Segoe UI", 13),
    fieldbackground="white"
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 13, "bold"),
    background="#1976D2",
    foreground="white",
    padding=8
)

style.map("Treeview",
          background=[("selected", "#E3F2FD")],
          foreground=[("selected", "#0D47A1")])


class ProductFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build_ui()
        self._load()

    def _build_ui(self):
        # ===== TITLE =====
        ctk.CTkLabel(
            self,
            text="QUẢN LÝ SẢN PHẨM",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=20, pady=(16, 10))

        # ===== TOOLBAR =====
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=20, pady=6)

        ctk.CTkButton(
            tb, text="Thêm",
            width=120, height=40,
            fg_color="#2E7D32", hover_color="#1B5E20",
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._add
        ).pack(side="right", padx=6)

        ctk.CTkButton(
            tb, text="Sửa",
            width=110, height=40,
            fg_color="#FB8C00", hover_color="#EF6C00",
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            command=self._edit
        ).pack(side="right", padx=6)

        ctk.CTkButton(
            tb, text="Xóa",
            width=110, height=40,
            fg_color="#E53935", hover_color="#C62828",
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            command=self._delete
        ).pack(side="right", padx=6)

        # ===== SEARCH =====
        sb = ctk.CTkFrame(self, fg_color="transparent")
        sb.pack(fill="x", padx=20, pady=(0, 10))

        self.ent_search = ctk.CTkEntry(
            sb,
            height=42,
            width=380,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            placeholder_text="Tìm theo tên hoặc mã sản phẩm..."
        )
        self.ent_search.pack(side="left")
        self.ent_search.bind("<KeyRelease>", lambda _: self._load())

        self.lbl_count = ctk.CTkLabel(
            sb,
            text="",
            text_color="gray",
            font=ctk.CTkFont(size=13)
        )
        self.lbl_count.pack(side="left", padx=12)

        # ===== TABLE =====
        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Mã", "Tên sản phẩm", "Loại", "Giá bán", "Tồn kho")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings")

        widths = [100, 320, 180, 130, 100]

        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _: self._edit())

    # ===== LOAD DATA =====
    def _load(self):
        kw = self.ent_search.get().strip()
        items = svc.search(kw) if kw else svc.get_all()

        for r in self.tree.get_children():
            self.tree.delete(r)

        for p in items:
            gia = f"{p.gia_ban:,.0f}đ"

            self.tree.insert(
                "", "end",
                iid=str(p.ma_sp),
                values=(p.ma_code, p.ten_sp, p.ten_loai, gia, p.ton_kho)
            )

        self.lbl_count.configure(text=f"{len(items)} sản phẩm")

    def _selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Thông báo", "Vui lòng chọn sản phẩm!")
            return None
        return int(sel[0])

    # ===== ACTION =====
    def _add(self):
        ProductDialog(self, None, self._load)

    def _edit(self):
        ma = self._selected()
        if ma:
            ProductDialog(self, ma, self._load)

    def _delete(self):
        ma = self._selected()
        if ma and messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa?"):
            svc.delete(ma)
            self._load()


# ===== DIALOG =====
class ProductDialog(ctk.CTkToplevel):
    def __init__(self, parent, ma_sp, callback):
        super().__init__(parent)
        self.ma_sp = ma_sp
        self.callback = callback

        self.title("Sản phẩm")
        self.geometry("420x420")
        self.resizable(False, False)
        self.grab_set()

        self._build()

    def _build(self):
        frm = ctk.CTkFrame(self, fg_color="transparent")
        frm.pack(fill="both", expand=True, padx=25, pady=20)

        def label(text):
            ctk.CTkLabel(frm, text=text,
                         font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(8, 2))

        def entry():
            e = ctk.CTkEntry(frm, height=38, corner_radius=8)
            e.pack(fill="x")
            return e

        label("Tên sản phẩm")
        self.e_name = entry()

        label("Giá bán")
        self.e_price = entry()

        label("Tồn kho")
        self.e_stock = entry()

        ctk.CTkButton(
            frm,
            text="Lưu",
            height=42,
            fg_color="#1976D2",
            hover_color="#1565C0",
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._save
        ).pack(fill="x", pady=18)

    def _save(self):
        messagebox.showinfo("Thông báo", "Demo UI - chưa xử lý backend")
        self.callback()
        self.destroy()