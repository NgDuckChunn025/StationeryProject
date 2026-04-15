import customtkinter as ctk
from tkinter import ttk, messagebox
from backend.models.invoice import Invoice
from backend.modules import product_service as psvc
from backend.modules import sales_service as ssvc
from backend.modules.pdf_exporter import export_invoice


# ===== STYLE TABLE =====
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="white",
    foreground="#1F2937",
    rowheight=36,
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


class SalesFrame(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self.invoice = Invoice(user["ma_nv"], user["ten_nv"])
        self._build_ui()
        self._load_products()

    # ================= UI =================
    def _build_ui(self):
        ctk.CTkLabel(
            self,
            text="BÁN HÀNG (POS)",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=20, pady=(16, 10))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self._build_left(main)
        self._build_right(main)

    # ================= LEFT =================
    def _build_left(self, parent):
        frm = ctk.CTkFrame(parent, corner_radius=12)
        frm.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            frm,
            text="Danh sách sản phẩm",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.ent_search = ctk.CTkEntry(
            frm,
            height=42,
            font=ctk.CTkFont(size=14),
            placeholder_text="Tìm tên hoặc mã sản phẩm..."
        )
        self.ent_search.pack(fill="x", padx=12, pady=(0, 6))
        self.ent_search.bind("<KeyRelease>", lambda _: self._load_products())

        cols = ("Mã", "Tên sản phẩm", "Giá bán", "Tồn kho")
        self.tree_sp = ttk.Treeview(frm, columns=cols, show="headings", height=16)

        widths = [100, 280, 130, 100]

        for col, w in zip(cols, widths):
            self.tree_sp.heading(col, text=col)
            self.tree_sp.column(col, width=w, anchor="center")

        self.tree_sp.pack(fill="both", expand=True, padx=12, pady=6)
        self.tree_sp.bind("<Double-1>", self._add_to_invoice)

        ctk.CTkLabel(
            frm,
            text="Double click để thêm vào hóa đơn",
            text_color="gray"
        ).pack(pady=(0, 10))

    # ================= RIGHT =================
    def _build_right(self, parent):
        frm = ctk.CTkFrame(parent, width=400, corner_radius=12)
        frm.pack(side="right", fill="y")
        frm.pack_propagate(False)

        ctk.CTkLabel(
            frm,
            text="HÓA ĐƠN",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(12, 6))

        cols = ("Tên SP", "Đơn giá", "SL", "Thành tiền")
        self.tree_hd = ttk.Treeview(frm, columns=cols, show="headings", height=12)

        self.tree_hd.column("Tên SP", width=150)
        for col in ("Đơn giá", "SL", "Thành tiền"):
            self.tree_hd.column(col, width=80, anchor="center")

        for col in cols:
            self.tree_hd.heading(col, text=col)

        self.tree_hd.pack(fill="x", padx=10, pady=4)

        # Xóa dòng
        ctk.CTkButton(
            frm,
            text="Xóa dòng",
            height=36,
            fg_color="#E53935",
            hover_color="#C62828",
            corner_radius=8,
            command=self._remove_item
        ).pack(padx=10, pady=4, fill="x")

        # Giảm giá
        gr = ctk.CTkFrame(frm, fg_color="transparent")
        gr.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(gr, text="Giảm giá:",
                     font=ctk.CTkFont(size=13)).pack(side="left")

        self.ent_discount = ctk.CTkEntry(
            gr,
            width=120,
            height=36
        )
        self.ent_discount.pack(side="right")
        self.ent_discount.insert(0, "0")
        self.ent_discount.bind("<KeyRelease>", lambda _: self._refresh_total())

        # Tổng tiền
        self.lbl_total = ctk.CTkLabel(
            frm,
            text="TỔNG: 0đ",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1565C0"
        )
        self.lbl_total.pack(pady=10)

        # Thanh toán
        ctk.CTkButton(
            frm,
            text="THANH TOÁN",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            corner_radius=10,
            command=self._checkout
        ).pack(fill="x", padx=10, pady=4)

        # Hóa đơn mới
        ctk.CTkButton(
            frm,
            text="Hóa đơn mới",
            height=38,
            fg_color="#FB8C00",
            hover_color="#EF6C00",
            corner_radius=8,
            command=self._new_invoice
        ).pack(fill="x", padx=10, pady=(0, 10))

    # ================= LOGIC =================
    def _load_products(self):
        kw = self.ent_search.get().strip()
        items = psvc.search(kw) if kw else psvc.get_all()

        for r in self.tree_sp.get_children():
            self.tree_sp.delete(r)

        for p in items:
            self.tree_sp.insert(
                "",
                "end",
                iid=str(p.ma_sp),
                values=(p.ma_code, p.ten_sp, p.fmt_gia_ban(), p.ton_kho)
            )

    def _add_to_invoice(self, _=None):
        sel = self.tree_sp.selection()
        if not sel:
            return

        vals = self.tree_sp.item(sel[0])["values"]

        popup = ctk.CTkInputDialog(
            text="Nhập số lượng:",
            title="Số lượng"
        )
        qty = popup.get_input()

        if not qty:
            return

        try:
            qty = int(qty)
        except:
            messagebox.showerror("Lỗi", "Số lượng không hợp lệ")
            return

        ma_sp = int(sel[0])
        ten_sp = vals[1]

        gia_ban = float(str(vals[2]).replace("đ", "").replace(",", ""))

        self.invoice.add_item(ma_sp, ten_sp, gia_ban, qty)
        self._refresh_invoice()

    def _remove_item(self):
        sel = self.tree_hd.selection()
        if sel:
            self.invoice.remove_item(int(sel[0]))
            self._refresh_invoice()

    def _refresh_invoice(self):
        for r in self.tree_hd.get_children():
            self.tree_hd.delete(r)

        for item in self.invoice.items:
            self.tree_hd.insert(
                "",
                "end",
                iid=str(item.ma_sp),
                values=item.to_table_row()
            )

        self._refresh_total()

    def _refresh_total(self):
        try:
            self.invoice.giam_gia = float(self.ent_discount.get() or 0)
        except:
            self.invoice.giam_gia = 0

        self.lbl_total.configure(
            text=f"TỔNG: {self.invoice.thanh_toan:,.0f}đ"
        )

    def _checkout(self):
        if not self.invoice.items:
            messagebox.showwarning("Hóa đơn trống", "Vui lòng thêm sản phẩm!")
            return

        self._refresh_total()

        confirm = messagebox.askyesno(
            "Xác nhận",
            f"Tổng thanh toán: {self.invoice.thanh_toan:,.0f}đ\nXác nhận?"
        )
        if not confirm:
            return

        ok, result = ssvc.create_invoice(self.invoice)

        if ok:
            ma_hd = result
            messagebox.showinfo("Thành công", f"Hóa đơn #{ma_hd}")

            if messagebox.askyesno("Xuất PDF", "Xuất hóa đơn PDF?"):
                items = [(i.ten_sp, i.don_gia, i.so_luong, i.thanh_tien)
                         for i in self.invoice.items]

                export_invoice(
                    ma_hd,
                    self.invoice.ten_kh,
                    self.user["ten_nv"],
                    items,
                    self.invoice.tong_tien,
                    self.invoice.giam_gia,
                    f"hoa_don_{ma_hd}.pdf"
                )

            self._new_invoice()
        else:
            messagebox.showerror("Lỗi", str(result))

    def _new_invoice(self):
        self.invoice = Invoice(self.user["ma_nv"], self.user["ten_nv"])
        self._refresh_invoice()
        self.ent_discount.delete(0, "end")
        self.ent_discount.insert(0, "0")