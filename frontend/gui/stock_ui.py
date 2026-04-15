import customtkinter as ctk
from tkinter import ttk, messagebox
from backend.modules import product_service as psvc
from backend.modules import stock_service as ssvc

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

class StockFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self._build()
        self._load_products()
        self._load_history()

    def _build(self):
        ctk.CTkLabel(self, text="NHẬP KHO",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=10)

        box = ctk.CTkFrame(self)
        box.pack(fill="x", padx=20, pady=10)

        self.cmb = ctk.CTkComboBox(box, width=300, height=38)
        self.cmb.pack(side="left", padx=10, pady=10)

        self.ent_qty = ctk.CTkEntry(box, placeholder_text="Số lượng", width=150, height=38)
        self.ent_qty.pack(side="left", padx=10)

        ctk.CTkButton(box, text="Nhập",
                      fg_color="#2E7D32",
                      command=self._stock_in).pack(side="left", padx=10)

        cols = ("Mã", "Sản phẩm", "Số lượng", "Ngày")

        self.tree = ttk.Treeview(self, columns=cols, show="headings")

        widths = [80, 250, 120, 180]

        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

    def _load_products(self):
        try:
            self.products = psvc.get_all()
            self.map = {p.ten_sp: p.ma_sp for p in self.products}
            self.cmb.configure(values=list(self.map.keys()))
        except Exception as e:
            print("Lỗi load sản phẩm:", e)

    def _stock_in(self):
        ten_sp = self.cmb.get().strip()

        if not ten_sp:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn sản phẩm")
            return

        try:
            ma_sp = self.map[ten_sp]
        except KeyError:
            messagebox.showerror("Lỗi", "Sản phẩm không tồn tại")
            return

        try:
            sl = int(self.ent_qty.get())
            if sl <= 0:
                raise ValueError
        except:
            messagebox.showerror("Lỗi", "Số lượng phải là số > 0")
            return

        ok, msg = ssvc.stock_in(ma_sp, sl)
        messagebox.showinfo("Kết quả", msg)

        if ok:
            self._load_history()

    def _load_history(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        for row in ssvc.get_history():
            # đảm bảo đúng thứ tự cột
            self.tree.insert("", "end", values=(
                row[0],  # mã
                row[1],  # tên SP
                row[2],  # số lượng
                str(row[3])[:19]  # ngày cho đẹp
            ))