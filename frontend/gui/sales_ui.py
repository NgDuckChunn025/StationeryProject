# frontend/gui/sales_ui.py — POS nâng cấp: dùng điểm, shortcut bàn phím
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from frontend.gui.theme import *
from backend.models.invoice import Invoice
from backend.modules import product_service as psvc
from backend.modules import sales_service as ssvc
from backend.modules import customer_service as csvc
from backend.modules.pdf_exporter import export_invoice


class SalesFrame(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user     = user
        self.invoice  = Invoice(user["ma_nv"], user["ten_nv"])
        self._so_diem_dung = 0
        self._build_ui()
        self._load_products()
        self._load_customers()
        # Shortcut
        self.winfo_toplevel().bind("<F2>", lambda e: self._checkout())
        self.winfo_toplevel().bind("<F5>", lambda _: self._new_invoice())
        self.winfo_toplevel().bind("<Escape>", lambda _: self._new_invoice())

    def _build_ui(self):
        # Shortcut hint
        hint = ctk.CTkFrame(self, fg_color=PRIMARY_LIGHT,
                             corner_radius=0, height=28)
        hint.pack(fill="x")
        hint.pack_propagate(False)
        ctk.CTkLabel(hint,
                     text="⌨️  F2 = Thanh toán   F5 = Hóa đơn mới   "
                          "Esc = Reset   Double-click SP = Thêm vào HĐ",
                     font=ctk.CTkFont(size=FS_XS),
                     text_color=PRIMARY).pack(side="left", padx=SP_MD)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True,
                  padx=SP_MD, pady=SP_SM)
        self._build_left(main)
        self._build_right(main)

    def _build_left(self, parent):
        frm = make_card(parent)
        frm.pack(side="left", fill="both", expand=True,
                 padx=(0, SP_SM))

        # Search
        sb = ctk.CTkFrame(frm, fg_color="transparent")
        sb.pack(fill="x", padx=SP_MD, pady=(SP_MD, SP_SM))
        self.ent_search = ctk.CTkEntry(
            sb, height=BTN_MD,
            placeholder_text="🔍  Tìm mã / tên sản phẩm...",
            font=ctk.CTkFont(size=FS_MD),
            corner_radius=RADIUS_SM, border_color=BORDER)
        self.ent_search.pack(side="left", fill="x", expand=True)
        self.ent_search.bind("<KeyRelease>",
                              lambda _: self._load_products())

        self.lbl_sp_count = ctk.CTkLabel(
            sb, text="",
            font=ctk.CTkFont(size=FS_SM), text_color=TEXT_GRAY)
        self.lbl_sp_count.pack(side="right", padx=(SP_SM, 0))

        # Product table
        style   = ttk.Style()
        tv_name = apply_treeview_style(style)
        cols    = ("Mã", "Tên sản phẩm", "Giá bán", "Tồn")
        self.tree_sp = ttk.Treeview(
            frm, columns=cols, show="headings",
            style=tv_name, selectmode="browse")
        cfg = [
            ("Mã",           80,  "center"),
            ("Tên sản phẩm", 300, "center"),
            ("Giá bán",      110, "center"),
            ("Tồn",           65, "center"),
        ]
        for col, w, a in cfg:
            self.tree_sp.heading(col, text=col, anchor="center")
            self.tree_sp.column(col, width=w, anchor=a,
                                minwidth=w, stretch=False)
        self.tree_sp.tag_configure("odd",     background="#F7FAFF")
        self.tree_sp.tag_configure("even",    background="#FFFFFF")
        self.tree_sp.tag_configure("lowstock",foreground=DANGER,
                                   background=DANGER_LIGHT)

        sy = ttk.Scrollbar(frm, orient="vertical",
                            command=self.tree_sp.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree_sp.configure(yscrollcommand=sy.set)
        self.tree_sp.pack(side="left", fill="both", expand=True,
                          padx=(SP_SM, 0), pady=(0, SP_SM))
        sy.pack(side="right", fill="y", pady=(0, SP_SM),
                padx=(0, 4))
        self.tree_sp.bind("<Double-1>", self._add_item)
        self.tree_sp.bind("<Return>",   self._add_item)

    def _build_right(self, parent):
        frm = make_card(parent)
        frm.configure(width=420)
        frm.pack(side="right", fill="y")
        frm.pack_propagate(False)

        # Tiêu đề hóa đơn
        hdr = ctk.CTkFrame(frm, fg_color=PRIMARY,
                            corner_radius=0, height=42)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🧾  HÓA ĐƠN BÁN HÀNG",
                     font=ctk.CTkFont(size=FS_MD, weight="bold"),
                     text_color="white").pack(expand=True)

        body = ctk.CTkFrame(frm, fg_color=CARD)
        body.pack(fill="both", expand=True)

        # Khách hàng
        kh_f = ctk.CTkFrame(body, fg_color=PRIMARY_LIGHT,
                              corner_radius=RADIUS_SM)
        kh_f.pack(fill="x", padx=SP_MD, pady=(SP_MD, SP_SM))
        r = ctk.CTkFrame(kh_f, fg_color="transparent")
        r.pack(fill="x", padx=SP_SM, pady=SP_SM)
        ctk.CTkLabel(r, text="Khách hàng:",
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color=TEXT_SECOND,
                     width=90).pack(side="left")
        self.cmb_kh = ctk.CTkComboBox(
            r, values=["Khách lẻ"],
            height=BTN_SM, font=ctk.CTkFont(size=FS_SM),
            fg_color=CARD, border_color=BORDER,
            corner_radius=RADIUS_SM,
            command=self._on_kh_change)
        self.cmb_kh.pack(side="left", fill="x", expand=True)

        self.lbl_diem = ctk.CTkLabel(
            kh_f, text="",
            font=ctk.CTkFont(size=FS_XS),
            text_color=PURPLE, anchor="w")
        self.lbl_diem.pack(anchor="w",
                            padx=SP_MD, pady=(0, SP_SM))

        # Items table
        style   = ttk.Style()
        tv_name = apply_treeview_style(style)
        cols    = ("Tên SP", "Đơn giá", "SL", "Thành tiền")
        self.tree_hd = ttk.Treeview(
            body, columns=cols, show="headings",
            style=tv_name, height=11)
        self.tree_hd.column("Tên SP",     width=155, anchor="center",      stretch=False)
        self.tree_hd.column("Đơn giá",    width=88,  anchor="center",      stretch=False)
        self.tree_hd.column("SL",         width=44,  anchor="center", stretch=False)
        self.tree_hd.column("Thành tiền", width=100, anchor="center",      stretch=False)
        for c in cols:
            self.tree_hd.heading(c, text=c, anchor="center")
        self.tree_hd.pack(fill="x", padx=SP_MD)
        self.tree_hd.bind("<Delete>",     self._remove_item)
        self.tree_hd.bind("<BackSpace>",  self._remove_item)

        make_btn(body, "Xóa dòng (Delete)", self._remove_item,
                 "danger", height=BTN_SM, icon="🗑").pack(
            fill="x", padx=SP_MD, pady=4)

        # Discount / Điểm
        disc_f = ctk.CTkFrame(body, fg_color=CARD)
        disc_f.pack(fill="x", padx=SP_MD, pady=4)

        ctk.CTkLabel(disc_f, text="Giảm giá (đ):",
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color=TEXT_SECOND).pack(side="left")
        self.ent_giam = ctk.CTkEntry(
            disc_f, width=100, height=BTN_SM,
            placeholder_text="0",
            fg_color=CARD, border_color=BORDER,
            corner_radius=RADIUS_SM)
        self.ent_giam.pack(side="left", padx=SP_SM)
        self.ent_giam.bind("<KeyRelease>",
                            lambda _: self._refresh_total())

        make_btn(disc_f, "Dùng điểm", self._dung_diem,
                 "purple", height=BTN_SM, icon="🎯").pack(
            side="right")

        self.lbl_giam_info = ctk.CTkLabel(
            body, text="",
            font=ctk.CTkFont(size=FS_XS, weight="bold"),
            text_color=PURPLE, anchor="w")
        self.lbl_giam_info.pack(anchor="w",
                                 padx=SP_MD, pady=(0, SP_SM))

        # Hình thức TT
        ht_f = ctk.CTkFrame(body, fg_color=CARD)
        ht_f.pack(fill="x", padx=SP_MD, pady=(0, SP_SM))
        ctk.CTkLabel(ht_f, text="Hình thức:",
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color=TEXT_SECOND).pack(side="left")
        self.cmb_httt = ctk.CTkComboBox(
            ht_f,
            values=["Tiền mặt","Chuyển khoản","Quẹt thẻ"],
            height=BTN_SM, font=ctk.CTkFont(size=FS_SM),
            fg_color=CARD, border_color=BORDER,
            corner_radius=RADIUS_SM)
        self.cmb_httt.pack(side="left", padx=SP_SM)
        self.cmb_httt.set("Tiền mặt")

        # Tổng
        total_f = ctk.CTkFrame(body, fg_color=SUCCESS_LIGHT,
                                corner_radius=RADIUS_SM)
        total_f.pack(fill="x", padx=SP_MD, pady=SP_SM)
        self.lbl_total = ctk.CTkLabel(
            total_f, text="THANH TOÁN:  0đ",
            font=ctk.CTkFont(size=FS_LG, weight="bold"),
            text_color=SUCCESS)
        self.lbl_total.pack(pady=SP_MD)

        # Actions
        make_btn(body, "THANH TOÁN  (F2)", self._checkout,
                 "success", height=BTN_LG, icon="✅").pack(
            fill="x", padx=SP_MD, pady=4)
        make_btn(body, "Hóa đơn mới  (F5)", self._new_invoice,
                 "ghost", height=BTN_MD, icon="🔄").pack(
            fill="x", padx=SP_MD)

    # ── Helpers ───────────────────────────────────────────────
    def _load_products(self):
        kw    = self.ent_search.get().strip()
        items = psvc.search(kw) if kw else psvc.get_all()
        for r in self.tree_sp.get_children():
            self.tree_sp.delete(r)
        for i, p in enumerate(items):
            tag = "lowstock" if p.sap_het \
                  else ("odd" if i%2 else "even")
            self.tree_sp.insert(
                "", "end", iid=str(p.ma_sp),
                values=(p.ma_code, p.ten_sp,
                        p.fmt_gia_ban(), p.ton_kho),
                tags=(tag,))
        self.lbl_sp_count.configure(
            text=f"{len(items)} sản phẩm")

    def _load_customers(self):
        kh_list = csvc.get_all()
        self._kh_map = {"Khách lẻ": None}
        self._kh_diem = {}
        for kh in kh_list:
            key = f"{kh.ten_kh} ({kh.so_dt})"
            self._kh_map[key] = kh.ma_kh
            self._kh_diem[kh.ma_kh] = kh.diem_tich_luy
        self.cmb_kh.configure(values=list(self._kh_map.keys()))

    def _on_kh_change(self, val):
        ma_kh = self._kh_map.get(val)
        self.invoice.ma_kh  = ma_kh
        self.invoice.ten_kh = val
        diem = self._kh_diem.get(ma_kh, 0) if ma_kh else 0
        self.lbl_diem.configure(
            text=f"🎯  {diem:,} điểm tích lũy" if diem > 0 else "")
        # Reset điểm dùng
        self._so_diem_dung  = 0
        self.invoice.giam_gia = 0
        self.lbl_giam_info.configure(text="")
        self._refresh_total()

    def _add_item(self, _=None):
        sel = self.tree_sp.selection()
        if not sel:
            return
        v      = self.tree_sp.item(sel[0])["values"]
        ma_sp  = int(sel[0])
        ten_sp = str(v[1])
        gia    = float(str(v[2]).replace("đ","").replace(",",""))

        dlg = ctk.CTkInputDialog(
            text=f"Số lượng ({ten_sp}):",
            title="Nhập số lượng")
        qty = dlg.get_input()
        if not qty:
            return
        try:
            qty = int(qty)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên dương!")
            return

        self.invoice.add_item(ma_sp, ten_sp, gia, qty)
        self._refresh_table()

    def _remove_item(self, _=None):
        sel = self.tree_hd.selection()
        if sel:
            self.invoice.remove_item(int(sel[0]))
            self._refresh_table()

    def _refresh_table(self):
        for r in self.tree_hd.get_children():
            self.tree_hd.delete(r)
        for item in self.invoice.items:
            self.tree_hd.insert("", "end", iid=str(item.ma_sp),
                                 values=item.to_table_row())
        self._refresh_total()

    def _refresh_total(self):
        try:
            giam_manual = float(
                self.ent_giam.get().strip() or 0)
        except ValueError:
            giam_manual = 0
        diem_giam = (self._so_diem_dung *
                     self._get_doi_diem())
        self.invoice.giam_gia = giam_manual + diem_giam
        tt = self.invoice.thanh_toan
        self.lbl_total.configure(
            text=f"THANH TOÁN:  {tt:,.0f}đ")

    def _get_doi_diem(self) -> float:
        try:
            from backend.modules.config_service import get_int
            return float(get_int("doi_diem", 1000))
        except Exception:
            return 1000.0

    def _dung_diem(self):
        if not self.invoice.items:
            return
        ma_kh = self.invoice.ma_kh
        if not ma_kh:
            messagebox.showwarning(
                "Chưa chọn KH",
                "Vui lòng chọn khách hàng để dùng điểm!")
            return
        diem_co   = self._kh_diem.get(ma_kh, 0)
        doi_diem  = self._get_doi_diem()
        if diem_co <= 0:
            messagebox.showinfo(
                "Không có điểm",
                "Khách hàng chưa có điểm tích lũy!")
            return
        max_diem = min(diem_co,
                       int(self.invoice.tong_tien * 0.3
                           / doi_diem))
        if max_diem <= 0:
            return
        dlg = ctk.CTkInputDialog(
            text=f"Có {diem_co:,} điểm\n"
                 f"(1 điểm = {doi_diem:,.0f}đ giảm)\n"
                 f"Tối đa {max_diem:,} điểm\n"
                 f"Nhập số điểm muốn dùng:",
            title="Dùng điểm tích lũy")
        val = dlg.get_input()
        if not val:
            return
        try:
            so_diem = max(0, min(int(val), max_diem))
        except ValueError:
            return
        self._so_diem_dung = so_diem
        giam = so_diem * doi_diem
        self.lbl_giam_info.configure(
            text=f"🎯  Dùng {so_diem:,} điểm → giảm {giam:,.0f}đ")
        self._refresh_total()

    def _new_invoice(self):
        self.invoice = Invoice(
            self.user["ma_nv"], self.user["ten_nv"])
        self._so_diem_dung = 0
        self._refresh_table()
        self.cmb_kh.set("Khách lẻ")
        self.lbl_diem.configure(text="")
        self.lbl_giam_info.configure(text="")
        self.ent_giam.delete(0, "end")
        self.cmb_httt.set("Tiền mặt")
        self.ent_search.delete(0, "end")
        self._load_products()

    def _checkout(self):
        if not self.invoice.items:
            messagebox.showwarning("Hóa đơn trống",
                                   "Vui lòng thêm sản phẩm!")
            return
        try:
            giam_manual = float(self.ent_giam.get() or 0)
        except ValueError:
            giam_manual = 0
        diem_giam = self._so_diem_dung * self._get_doi_diem()
        self.invoice.giam_gia  = giam_manual + diem_giam
        self.invoice.hinh_thuc = self.cmb_httt.get()

        tt = self.invoice.thanh_toan
        msg = (f"Khách: {self.invoice.ten_kh}\n"
               f"Tổng: {self.invoice.tong_tien:,.0f}đ")
        if self.invoice.giam_gia > 0:
            msg += f"\nGiảm: {self.invoice.giam_gia:,.0f}đ"
        msg += f"\nThanh toán: {tt:,.0f}đ"

        if not messagebox.askyesno("Xác nhận thanh toán", msg):
            return

        ok, result = ssvc.create_invoice(self.invoice)
        if not ok:
            messagebox.showerror("Lỗi thanh toán", str(result))
            return

        ma_hd = result
        # Tích điểm + trừ điểm
        if self.invoice.ma_kh:
            try:
                from backend.modules.config_service import get_int
                ty_le = get_int("ty_le_tich_diem", 10000)
                diem_them = int(tt // ty_le)
                csvc.add_points(self.invoice.ma_kh,
                                 diem_them - self._so_diem_dung)
                self._kh_diem[self.invoice.ma_kh] = max(
                    0, self._kh_diem.get(self.invoice.ma_kh,0)
                       + diem_them - self._so_diem_dung)
            except Exception:
                pass

        # Hỏi xuất PDF
        if messagebox.askyesno(
            "Thành công!",
            f"HĐ #{ma_hd:04d} đã lưu!\nXuất PDF hóa đơn?"
        ):
            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=f"HD_{ma_hd:04d}.pdf",
                filetypes=[("PDF", "*.pdf"), ("All", "*.*")])
            if path:
                items = [(i.ten_sp, i.don_gia,
                          i.so_luong, i.thanh_tien)
                         for i in self.invoice.items]
                export_invoice(
                    ma_hd, self.invoice.ten_kh,
                    self.invoice.ten_nv, items,
                    self.invoice.tong_tien,
                    self.invoice.giam_gia, path,
                    self.invoice.hinh_thuc)
        self._new_invoice()