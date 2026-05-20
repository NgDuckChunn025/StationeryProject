# frontend/gui/invoice_history_ui.py
# ================================================================
# Lịch sử hóa đơn — xem, lọc, xem chi tiết, in lại PDF
# ================================================================
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import date, timedelta
from frontend.gui.theme import (
    apply_treeview_style, make_btn, page_header, make_card,
    SP_SM, SP_MD, SP_LG, SP_XL,
    FS_XS, FS_SM, FS_MD, FS_LG,
    BTN_SM, BTN_MD, BTN_LG,
    RADIUS_SM, RADIUS_LG,
    PRIMARY, PRIMARY_LIGHT, SUCCESS, WARNING,
    DANGER, CARD, BORDER,
    TEXT_PRIMARY, TEXT_SECOND, TEXT_GRAY,
)
from backend.modules import sales_service as ssvc
from backend.modules.pdf_exporter import export_invoice


class InvoiceHistoryFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._data = []
        self._build_ui()
        self._quick_range(29)   # Mặc định 30 ngày

    # ── Build ──────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=SP_LG, pady=(SP_LG, SP_SM))
        page_header(tb, "📋  Lịch sử Hóa đơn",
                    "Tra cứu, xem chi tiết và in lại hóa đơn"
                    ).pack(side="left")

        # Thanh lọc
        bar = make_card(self)
        bar.pack(fill="x", padx=SP_LG, pady=(0, SP_SM))
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=SP_MD, pady=SP_SM)

        ctk.CTkLabel(inner, text="Khoảng nhanh:",
                     font=ctk.CTkFont(size=FS_SM)).pack(side="left")
        for txt, days in [("Hôm nay", 0), ("7 ngày", 6),
                           ("30 ngày", 29), ("Tháng này", -1)]:
            make_btn(inner, txt, lambda d=days: self._quick_range(d),
                     "ghost", height=BTN_SM).pack(
                side="left", padx=3)

        ctk.CTkLabel(inner, text="Từ:",
                     font=ctk.CTkFont(size=FS_SM)).pack(
            side="left", padx=(12, 4))
        self.ent_from = ctk.CTkEntry(inner, width=110, height=BTN_SM,
                                      placeholder_text="YYYY-MM-DD")
        self.ent_from.pack(side="left")

        ctk.CTkLabel(inner, text="Đến:",
                     font=ctk.CTkFont(size=FS_SM)).pack(
            side="left", padx=(8, 4))
        self.ent_to = ctk.CTkEntry(inner, width=110, height=BTN_SM,
                                    placeholder_text="YYYY-MM-DD")
        self.ent_to.pack(side="left")

        make_btn(inner, "Xem", self._load, "primary",
                 height=BTN_SM, icon="🔍").pack(side="left", padx=8)

        # Tìm theo mã HĐ
        ctk.CTkLabel(inner, text="Mã HĐ:",
                     font=ctk.CTkFont(size=FS_SM)).pack(
            side="left", padx=(8, 4))
        self.ent_mahd = ctk.CTkEntry(inner, width=80, height=BTN_SM,
                                      placeholder_text="#0001")
        self.ent_mahd.pack(side="left")
        make_btn(inner, "Tìm", self._search_by_id, "ghost",
                 height=BTN_SM).pack(side="left", padx=4)

        # Summary row
        self.lbl_sum = ctk.CTkLabel(
            bar, text="",
            font=ctk.CTkFont(size=FS_SM, weight="bold"),
            text_color=TEXT_GRAY)
        self.lbl_sum.pack(anchor="e", padx=SP_MD, pady=(0, SP_SM))

        # Layout 2 cột
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True,
                  padx=SP_MD, pady=(0, SP_MD))
        self._build_list(main)
        self._build_detail(main)

    def _build_list(self, parent):
        frm = make_card(parent)
        frm.pack(side="left", fill="both", expand=True,
                 padx=(0, SP_SM))

        style  = ttk.Style()
        tv     = apply_treeview_style(style)
        cols   = ("Mã HĐ", "Khách hàng", "Nhân viên",
                  "Ngày bán", "Tổng tiền", "Hình thức")
        self.tree = ttk.Treeview(
            frm, columns=cols, show="headings",
            style=tv, selectmode="browse")
        cfg = [
            ("Mã HĐ",      70,  "center"),
            ("Khách hàng", 160, "center"),
            ("Nhân viên",  130, "center"),
            ("Ngày bán",   130, "center"),
            ("Tổng tiền",  120, "center"),
            ("Hình thức",  110, "center"),
        ]
        for col, w, a in cfg:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=w, anchor=a,
                             minwidth=w, stretch=False)
        self.tree.tag_configure("odd",  background="#F7FAFF")
        self.tree.tag_configure("even", background="#FFFFFF")

        sy = ttk.Scrollbar(frm, orient="vertical",
                            command=self.tree.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=sy.set)
        self.tree.pack(side="left", fill="both", expand=True,
                       padx=(SP_SM, 0), pady=SP_SM)
        sy.pack(side="right", fill="y", pady=SP_SM, padx=(0, 4))
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>",         self._on_select)

    def _build_detail(self, parent):
        frm = make_card(parent)
        frm.configure(width=380)
        frm.pack(side="right", fill="y")
        frm.pack_propagate(False)

        ctk.CTkLabel(frm, text="🧾  Chi tiết hóa đơn",
                     font=ctk.CTkFont(size=FS_LG, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(
            pady=(SP_MD, SP_SM))

        # Info block
        info_f = ctk.CTkFrame(frm, fg_color=PRIMARY_LIGHT,
                               corner_radius=RADIUS_SM)
        info_f.pack(fill="x", padx=SP_MD, pady=(0, SP_SM))
        self.lbl_hd_info = ctk.CTkLabel(
            info_f, text="Chọn hóa đơn ở bên trái",
            font=ctk.CTkFont(size=FS_SM),
            text_color=TEXT_SECOND, justify="left")
        self.lbl_hd_info.pack(anchor="w", padx=SP_MD, pady=SP_SM)

        # Items
        style  = ttk.Style()
        tv     = apply_treeview_style(style)
        cols   = ("Tên SP", "Đơn giá", "SL", "Thành tiền")
        self.tree_det = ttk.Treeview(
            frm, columns=cols, show="headings",
            style=tv, height=12)
        self.tree_det.column("Tên SP",     width=200, anchor="center",      stretch=False)
        self.tree_det.column("Đơn giá",    width=120,  anchor="center",      stretch=False)
        self.tree_det.column("SL",         width=85,  anchor="center", stretch=False)
        self.tree_det.column("Thành tiền", width=130,  anchor="center",      stretch=False)
        for c in cols:
            self.tree_det.heading(c, text=c, anchor="center")
        self.tree_det.pack(fill="x", padx=SP_MD, pady=(0, SP_SM))

        # Tổng
        self.lbl_det_total = ctk.CTkLabel(
            frm, text="",
            font=ctk.CTkFont(size=FS_LG, weight="bold"),
            text_color=SUCCESS)
        self.lbl_det_total.pack(anchor="e", padx=SP_MD, pady=(0, SP_SM))

        # Buttons
        make_btn(frm, "In lại PDF", self._reprint_pdf,
                 "primary", height=BTN_MD, icon="🖨️").pack(
            fill="x", padx=SP_MD, pady=4)

        self._sel_hd = None   # hóa đơn đang chọn

    # ── Helpers ───────────────────────────────────────────────
    def _quick_range(self, days: int):
        today = date.today()
        if days == -1:
            start = today.replace(day=1)
        elif days == 0:
            start = today
        else:
            start = today - timedelta(days=days)
        self.ent_from.delete(0, "end")
        self.ent_from.insert(0, str(start))
        self.ent_to.delete(0, "end")
        self.ent_to.insert(0, str(today))
        self._load()

    def _load(self):
        tu   = self.ent_from.get().strip()
        den  = self.ent_to.get().strip()
        data = ssvc.get_invoices(tu or None, den or None)
        self._fill_tree(data)

    def _search_by_id(self):
        txt = self.ent_mahd.get().strip().lstrip("#")
        if not txt:
            return
        try:
            ma_hd = int(txt)
        except ValueError:
            messagebox.showwarning("Lỗi", "Mã HĐ phải là số!")
            return
        data = ssvc.get_invoices()
        found = [r for r in data if r[0] == ma_hd]
        self._fill_tree(found)

    def _fill_tree(self, data: list):
        self._data = data
        for r in self.tree.get_children():
            self.tree.delete(r)
        tong = 0.0
        for i, row in enumerate(data):
            ma_hd, ten_kh, ten_nv, ngay, tong_t, giam, tt, httt = row[:8]
            tong += float(tt or 0)
            tag   = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=str(ma_hd),
                             values=(f"#{ma_hd:04d}", ten_kh, ten_nv,
                                     str(ngay)[:16],
                                     f"{float(tt or 0):,.0f}đ",
                                     httt or "Tiền mặt"),
                             tags=(tag,))
        self.lbl_sum.configure(
            text=f"{len(data)} hóa đơn  |  "
                 f"Tổng: {tong:,.0f}đ")

    def _on_select(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        ma_hd = int(sel[0])
        # Lấy thông tin hóa đơn từ data
        row = next((r for r in self._data if r[0] == ma_hd), None)
        if not row:
            return
        self._sel_hd = row

        ma_hd, ten_kh, ten_nv, ngay, tong_t, giam, tt, httt = row[:8]
        info = (f"Mã HĐ: #{ma_hd:04d}\n"
                f"Khách: {ten_kh}\n"
                f"NV: {ten_nv}\n"
                f"Ngày: {str(ngay)[:16]}\n"
                f"HT: {httt or 'Tiền mặt'}\n"
                f"Giảm: {float(giam or 0):,.0f}đ")
        self.lbl_hd_info.configure(text=info)

        # Load chi tiết
        det = ssvc.get_invoice_detail(ma_hd)
        for r in self.tree_det.get_children():
            self.tree_det.delete(r)
        for d in det:
            self.tree_det.insert("", "end",
                                  values=(d[0],
                                          f"{float(d[1]):,.0f}đ",
                                          d[2],
                                          f"{float(d[3]):,.0f}đ"))
        self.lbl_det_total.configure(
            text=f"Thanh toán: {float(tt or 0):,.0f}đ")

    def _reprint_pdf(self):
        if not self._sel_hd:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn hóa đơn!")
            return
        row    = self._sel_hd
        ma_hd  = row[0]
        ten_kh = row[1]
        ten_nv = row[2]
        tong   = float(row[4] or 0)
        giam   = float(row[5] or 0)
        httt   = row[7] or "Tiền mặt"

        det = ssvc.get_invoice_detail(ma_hd)
        items = [(d[0], d[1], d[2], d[3]) for d in det]

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"hoa_don_{ma_hd:04d}.pdf",
            filetypes=[("PDF", "*.pdf"), ("Tất cả", "*.*")])
        if not path:
            return
        ok = export_invoice(ma_hd, ten_kh, ten_nv,
                            items, tong, giam, path, httt)
        if ok:
            messagebox.showinfo("Thành công", f"Đã lưu PDF:\n{path}")
        else:
            messagebox.showerror("Lỗi", "Không xuất được PDF!")

    def _open_return(self):
        if not self._sel_hd:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn hóa đơn!")
            return
        # Import lazy để tránh circular
        from frontend.gui.return_ui import ReturnDialog
        ma_hd = self._sel_hd[0]
        ReturnDialog(self, ma_hd,
                     callback=lambda: None)
