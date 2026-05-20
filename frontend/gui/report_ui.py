# frontend/gui/report_ui.py — nâng cấp: lợi nhuận, tồn kho, cảnh báo
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import date, timedelta
from frontend.gui.theme import (
    apply_treeview_style, make_btn, page_header, make_card,
    SP_SM, SP_MD, SP_LG, SP_XL,
    FS_XS, FS_SM, FS_MD, FS_LG,
    BTN_SM, BTN_MD, BTN_LG, RADIUS_SM,
    PRIMARY, PRIMARY_LIGHT, SUCCESS, SUCCESS_LIGHT,
    WARNING, WARNING_LIGHT, DANGER, DANGER_LIGHT,
    CARD, BORDER, BG,
    TEXT_PRIMARY, TEXT_SECOND, TEXT_GRAY,
)
from backend.modules import report_service as rsvc


class ReportFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._data_dt  = []
        self._data_loi = []
        self._build_ui()
        self._quick_range(29)

    def _build_ui(self):
        # Header + quick actions
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=SP_LG, pady=(SP_LG, SP_SM))
        page_header(tb, "📈  Báo cáo & Thống kê",
                    "Doanh thu, lợi nhuận, tồn kho và sản phẩm bán chạy"
                    ).pack(side="left")

        # Filter bar
        bar = make_card(self)
        bar.pack(fill="x", padx=SP_LG, pady=(0, SP_SM))
        row1 = ctk.CTkFrame(bar, fg_color="transparent")
        row1.pack(fill="x", padx=SP_MD, pady=(SP_SM, 4))

        ctk.CTkLabel(row1, text="Khoảng nhanh:",
                     font=ctk.CTkFont(size=FS_SM)).pack(side="left")
        for txt, days in [("Hôm nay", 0), ("7 ngày", 6),
                           ("30 ngày", 29), ("Tháng này", -1)]:
            make_btn(row1, txt, lambda d=days: self._quick_range(d),
                     "ghost", height=BTN_SM).pack(side="left", padx=3)

        ctk.CTkLabel(row1, text="Từ:", font=ctk.CTkFont(size=FS_SM)
                     ).pack(side="left", padx=(12, 4))
        self.ent_from = ctk.CTkEntry(row1, width=110, height=BTN_SM)
        self.ent_from.pack(side="left")
        ctk.CTkLabel(row1, text="Đến:", font=ctk.CTkFont(size=FS_SM)
                     ).pack(side="left", padx=(8, 4))
        self.ent_to = ctk.CTkEntry(row1, width=110, height=BTN_SM)
        self.ent_to.pack(side="left")
        make_btn(row1, "Xem", self._load, "primary",
                 height=BTN_SM, icon="🔍").pack(side="left", padx=8)

        # Export buttons
        make_btn(row1, "Excel", self._export_excel,
                 "success", height=BTN_SM, icon="📊").pack(side="right", padx=4)
        make_btn(row1, "Biểu đồ DT", lambda: self._show_chart("revenue"),
                 "purple", height=BTN_SM, icon="📉").pack(side="right", padx=4)
        make_btn(row1, "Biểu đồ LN", lambda: self._show_chart("profit"),
                 "warning", height=BTN_SM, icon="💹").pack(side="right", padx=4)

        # Summary cards
        self.sum_row = ctk.CTkFrame(bar, fg_color="transparent")
        self.sum_row.pack(fill="x", padx=SP_MD, pady=(0, SP_SM))
        self._make_sum_cards()

        # Tabs
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True,
                       padx=SP_LG, pady=(0, SP_LG))
        t1 = self.tabs.add("📅  Doanh thu theo ngày")
        t2 = self.tabs.add("💰  Lợi nhuận theo ngày")
        t3 = self.tabs.add("🏆  Top sản phẩm")
        t4 = self.tabs.add("📦  Tồn kho")
        t5 = self.tabs.add("⚠️  Sắp hết hàng")

        self._build_tab_dt(t1)
        self._build_tab_loi(t2)
        self._build_tab_top(t3)
        self._build_tab_inv(t4)
        self._build_tab_low(t5)

    def _make_sum_cards(self):
        for w in self.sum_row.winfo_children():
            w.destroy()
        cards = [
            ("💰", "Tổng DT",   "0đ",   SUCCESS,  SUCCESS_LIGHT),
            ("📈", "Lợi nhuận", "0đ",   PRIMARY,  PRIMARY_LIGHT),
            ("🧾", "Hóa đơn",   "0",    WARNING,  WARNING_LIGHT),
            ("📦", "Đã bán",    "0 SP", DANGER,   DANGER_LIGHT),
        ]
        for icon, lbl, val, color, bg in cards:
            f = ctk.CTkFrame(self.sum_row, fg_color=bg,
                              corner_radius=8, border_width=1,
                              border_color=color)
            f.pack(side="left", fill="x", expand=True, padx=4)
            ctk.CTkLabel(f, text=icon,
                         font=ctk.CTkFont(size=18)).pack(pady=(8,2))
            lbl_val = ctk.CTkLabel(f, text=val,
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    text_color=color)
            lbl_val.pack()
            ctk.CTkLabel(f, text=lbl,
                         font=ctk.CTkFont(size=FS_XS),
                         text_color=TEXT_SECOND).pack(pady=(0, 8))
            # Lưu reference để update
            setattr(self, f"_sum_{lbl.replace(' ','_')}", lbl_val)

    # ── Tabs ──────────────────────────────────────────────────
    def _build_tab_dt(self, parent):
        style  = ttk.Style()
        tv     = apply_treeview_style(style)
        cols   = ("Ngày", "Số HĐ", "Doanh thu (đ)", "Trung bình/HĐ")
        self.tree_dt = ttk.Treeview(parent, columns=cols,
                                     show="headings", style=tv)
        cfg = [("Ngày",160,"center"),("Số HĐ",100,"center"),
               ("Doanh thu (đ)",220,"center"),("Trung bình/HĐ",180,"center")]
        for col, w, a in cfg:
            self.tree_dt.heading(col, text=col, anchor="center")
            self.tree_dt.column(col, width=w, anchor=a,
                                minwidth=w, stretch=False)
        self.tree_dt.tag_configure("odd",  background="#F7FAFF")
        self.tree_dt.tag_configure("even", background="#FFFFFF")
        self.tree_dt.tag_configure("high", foreground=SUCCESS)
        sy = ttk.Scrollbar(parent, orient="vertical",
                            command=self.tree_dt.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree_dt.configure(yscrollcommand=sy.set)
        self.tree_dt.pack(side="left", fill="both", expand=True,
                          padx=(SP_SM,0), pady=SP_SM)
        sy.pack(side="right", fill="y", pady=SP_SM, padx=(0,4))

    def _build_tab_loi(self, parent):
        style  = ttk.Style()
        tv     = apply_treeview_style(style)
        cols   = ("Ngày","Doanh thu (đ)","Giá vốn (đ)",
                  "Lợi nhuận (đ)","Tỉ lệ LN%")
        self.tree_loi = ttk.Treeview(parent, columns=cols,
                                      show="headings", style=tv)
        cfg = [("Ngày",130,"center"),("Doanh thu (đ)",160,"center"),
               ("Giá vốn (đ)",150,"center"),("Lợi nhuận (đ)",150,"center"),
               ("Tỉ lệ LN%",110,"center")]
        for col, w, a in cfg:
            self.tree_loi.heading(col, text=col, anchor="center")
            self.tree_loi.column(col, width=w, anchor=a,
                                 minwidth=w, stretch=False)
        self.tree_loi.tag_configure("profit",  foreground=SUCCESS)
        self.tree_loi.tag_configure("loss",    foreground=DANGER)
        self.tree_loi.tag_configure("odd",     background="#F7FAFF")
        self.tree_loi.tag_configure("even",    background="#FFFFFF")
        sy = ttk.Scrollbar(parent, orient="vertical",
                            command=self.tree_loi.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree_loi.configure(yscrollcommand=sy.set)
        self.tree_loi.pack(side="left", fill="both", expand=True,
                           padx=(SP_SM,0), pady=SP_SM)
        sy.pack(side="right", fill="y", pady=SP_SM, padx=(0,4))

    def _build_tab_top(self, parent):
        style  = ttk.Style()
        tv     = apply_treeview_style(style)
        cols   = ("Hạng","Tên sản phẩm","Số lượng bán","Doanh thu (đ)")
        self.tree_top = ttk.Treeview(parent, columns=cols,
                                      show="headings", style=tv)
        cfg = [("Hạng",55,"center"),("Tên sản phẩm",300,"center"),
               ("Số lượng bán",130,"center"),("Doanh thu (đ)",190,"center")]
        for col, w, a in cfg:
            self.tree_top.heading(col, text=col, anchor="center")
            self.tree_top.column(col, width=w, anchor=a,
                                 minwidth=w, stretch=False)
        self.tree_top.tag_configure("gold",   foreground="#B8860B",background="#FFFDE7")
        self.tree_top.tag_configure("silver", foreground="#607D8B",background="#F5F5F5")
        self.tree_top.tag_configure("bronze", foreground="#8D4E1D",background="#FBE9E7")
        self.tree_top.tag_configure("odd",    background="#F7FAFF")
        self.tree_top.tag_configure("even",   background="#FFFFFF")
        sy = ttk.Scrollbar(parent, orient="vertical",
                            command=self.tree_top.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree_top.configure(yscrollcommand=sy.set)
        self.tree_top.pack(side="left", fill="both", expand=True,
                           padx=(SP_SM,0), pady=SP_SM)
        sy.pack(side="right", fill="y", pady=SP_SM, padx=(0,4))

    def _build_tab_inv(self, parent):
        style  = ttk.Style()
        tv     = apply_treeview_style(style)
        cols   = ("Loại SP","Số SP","Tổng tồn",
                  "Giá trị nhập (đ)","Giá trị bán (đ)")
        self.tree_inv = ttk.Treeview(parent, columns=cols,
                                      show="headings", style=tv)
        cfg = [("Loại SP",160,"center"),("Số SP",80,"center"),
               ("Tổng tồn",100,"center"),
               ("Giá trị nhập (đ)",180,"center"),
               ("Giá trị bán (đ)",180,"center")]
        for col, w, a in cfg:
            self.tree_inv.heading(col, text=col, anchor="center")
            self.tree_inv.column(col, width=w, anchor=a,
                                 minwidth=w, stretch=False)
        self.tree_inv.tag_configure("odd",  background="#F7FAFF")
        self.tree_inv.tag_configure("even", background="#FFFFFF")
        sy = ttk.Scrollbar(parent, orient="vertical",
                            command=self.tree_inv.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree_inv.configure(yscrollcommand=sy.set)
        self.tree_inv.pack(side="left", fill="both", expand=True,
                           padx=(SP_SM,0), pady=SP_SM)
        sy.pack(side="right", fill="y", pady=SP_SM, padx=(0,4))

    def _build_tab_low(self, parent):
        style  = ttk.Style()
        tv     = apply_treeview_style(style)
        cols   = ("Mã SP","Tên sản phẩm","Loại",
                  "Tồn kho","Ngưỡng","Giá nhập")
        self.tree_low = ttk.Treeview(parent, columns=cols,
                                      show="headings", style=tv)
        cfg = [("Mã SP",80,"center"),("Tên sản phẩm",240,"center"),
               ("Loại",120,"center"),("Tồn kho",90,"center"),
               ("Ngưỡng",80,"center"),("Giá nhập",120,"center")]
        for col, w, a in cfg:
            self.tree_low.heading(col, text=col, anchor="center")
            self.tree_low.column(col, width=w, anchor=a,
                                 minwidth=w, stretch=False)
        self.tree_low.tag_configure("critical",
                                    foreground=DANGER,
                                    background=DANGER_LIGHT)
        self.tree_low.tag_configure("warning",
                                    foreground=WARNING,
                                    background=WARNING_LIGHT)
        sy = ttk.Scrollbar(parent, orient="vertical",
                            command=self.tree_low.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree_low.configure(yscrollcommand=sy.set)
        self.tree_low.pack(side="left", fill="both", expand=True,
                           padx=(SP_SM,0), pady=SP_SM)
        sy.pack(side="right", fill="y", pady=SP_SM, padx=(0,4))

        make_btn(parent, "Làm mới", self._load_low,
                 "ghost", height=BTN_SM, icon="🔄").pack(
            anchor="e", padx=SP_MD, pady=SP_SM)

    # ── Load data ─────────────────────────────────────────────
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
        tu  = self.ent_from.get().strip()
        den = self.ent_to.get().strip()

        # Tab 1: Doanh thu
        self._data_dt = rsvc.revenue_by_day(tu, den)
        for r in self.tree_dt.get_children(): self.tree_dt.delete(r)
        tong_dt = 0; tong_hd = 0
        vals_dt = [float(r[2] or 0) for r in self._data_dt]
        max_dt  = max(vals_dt) if vals_dt else 0
        for i, row in enumerate(self._data_dt):
            ngay, so_hd, dt = row
            dt  = float(dt or 0); tong_dt += dt; tong_hd += int(so_hd)
            avg = dt / max(int(so_hd), 1)
            tag = "high" if dt == max_dt and dt > 0 \
                  else ("odd" if i%2 else "even")
            self.tree_dt.insert("", "end",
                                values=(str(ngay), int(so_hd),
                                        f"{dt:,.0f}đ",
                                        f"{avg:,.0f}đ"),
                                tags=(tag,))

        # Tab 2: Lợi nhuận
        self._data_loi = rsvc.profit_by_day(tu, den)
        for r in self.tree_loi.get_children(): self.tree_loi.delete(r)
        tong_loi = 0
        for i, row in enumerate(self._data_loi):
            ngay, so_hd, doanh, von, loi = row
            loi  = float(loi or 0); tong_loi += loi
            ty_le = (loi/float(doanh)*100) if doanh else 0
            tag  = "profit" if loi >= 0 else "loss"
            self.tree_loi.insert("", "end",
                                 values=(str(ngay),
                                         f"{float(doanh or 0):,.0f}đ",
                                         f"{float(von or 0):,.0f}đ",
                                         f"{loi:,.0f}đ",
                                         f"{ty_le:.1f}%"),
                                 tags=(tag,))

        # Summary cards
        try:
            self._sum_Tổng_DT.configure(
                text=f"{tong_dt/1e6:.1f}M" if tong_dt>=1e6
                     else f"{tong_dt:,.0f}đ")
            self._sum_Lợi_nhuận.configure(
                text=f"{tong_loi/1e6:.1f}M" if abs(tong_loi)>=1e6
                     else f"{tong_loi:,.0f}đ")
            self._sum_Hóa_đơn.configure(text=str(tong_hd))
        except Exception:
            pass

        # Tab 3: Top SP
        top = rsvc.top_products(15)
        for r in self.tree_top.get_children(): self.tree_top.delete(r)
        tong_ban = 0
        medals = {0:"🥇",1:"🥈",2:"🥉"}
        tag_map = {0:"gold",1:"silver",2:"bronze"}
        for i, (ten, sl, dt) in enumerate(top):
            tong_ban += int(sl)
            rank = medals.get(i, str(i+1))
            tag  = tag_map.get(i, "odd" if i%2 else "even")
            self.tree_top.insert("", "end",
                                 values=(rank, ten, int(sl),
                                         f"{float(dt or 0):,.0f}đ"),
                                 tags=(tag,))
        try:
            self._sum_Đã_bán.configure(text=f"{tong_ban} SP")
        except Exception:
            pass

        # Tab 4: Tồn kho
        inv = rsvc.inventory_report()
        for r in self.tree_inv.get_children(): self.tree_inv.delete(r)
        for i, row in enumerate(inv):
            loai, so_sp, tong_ton, gtn, gtb = row
            tag = "odd" if i%2 else "even"
            self.tree_inv.insert("", "end",
                                  values=(loai or "Chưa phân loại",
                                          int(so_sp or 0),
                                          int(tong_ton or 0),
                                          f"{float(gtn or 0):,.0f}đ",
                                          f"{float(gtb or 0):,.0f}đ"),
                                  tags=(tag,))

        self._load_low()

    def _load_low(self):
        rows = rsvc.low_stock_products()
        for r in self.tree_low.get_children(): self.tree_low.delete(r)
        for row in rows:
            ma_code, ten, loai, ton, nguong, gia = row
            tag = "critical" if ton == 0 else "warning"
            self.tree_low.insert("", "end",
                                  values=(ma_code, ten, loai,
                                          ton, nguong,
                                          f"{float(gia or 0):,.0f}đ"),
                                  tags=(tag,))

    # ── Chart & Export ────────────────────────────────────────
    def _show_chart(self, mode: str = "revenue"):
        data = self._data_loi if mode == "profit" else self._data_dt
        if not data:
            messagebox.showwarning("Không có dữ liệu",
                                   "Vui lòng nhấn Xem trước!")
            return
        try:
            fig = rsvc.plot_revenue(data, mode=mode)
            from matplotlib.backends.backend_tkagg import (
                FigureCanvasTkAgg, NavigationToolbar2Tk)
            n   = len(data)
            w   = min(max(900, n*100), 1400)
            win = ctk.CTkToplevel(self)
            win.title("📊 Biểu đồ")
            win.geometry(f"{w}x540")
            win.grab_set()
            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True,
                                        padx=8, pady=8)
            tb = NavigationToolbar2Tk(canvas, win)
            tb.update()
        except Exception as e:
            messagebox.showerror("Lỗi vẽ biểu đồ", str(e))

    def _export_excel(self):
        if not self._data_dt:
            messagebox.showwarning("Không có dữ liệu",
                                   "Vui lòng nhấn Xem trước!")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"doanh_thu_{date.today()}.xlsx",
            filetypes=[("Excel", "*.xlsx"), ("All", "*.*")])
        if not path:
            return
        ok = rsvc.export_excel(
            [(str(r[0]), int(r[1]), float(r[2] or 0))
             for r in self._data_dt],
            path,
            headers=["Ngày", "Số hóa đơn", "Doanh thu (đ)"])
        if ok:
            messagebox.showinfo("Thành công", f"Đã lưu:\n{path}")
        else:
            messagebox.showerror("Lỗi", "Không xuất được file Excel!")
