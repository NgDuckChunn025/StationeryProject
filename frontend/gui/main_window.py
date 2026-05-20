# frontend/gui/main_window.py
import traceback
import customtkinter as ctk
from tkinter import messagebox
from frontend.gui.theme import *
from backend.modules.auth_service import is_admin
from backend.modules.report_service import get_dashboard


class MainWindow(ctk.CTk):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.title("VPP Manager — Quản lý Cửa hàng Văn phòng phẩm")
        self.geometry("1440x820")
        self.minsize(1150, 660)
        self.eval("tk::PlaceWindow . center")
        self._build_ui()
        self._navigate("dashboard")

    def _build_ui(self):
        # ── Sidebar ───────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=200,
                                     corner_radius=0,
                                     fg_color="#0F172A")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo block
        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.pack(fill="x", padx=12, pady=(18, 10))
        ctk.CTkLabel(logo, text="🛒",
                     font=ctk.CTkFont(size=30)).pack()
        ctk.CTkLabel(logo, text="VPP Manager",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="white").pack(pady=(2,0))
        ctk.CTkLabel(logo, text="Văn phòng phẩm",
                     font=ctk.CTkFont(size=FS_XS),
                     text_color="#A8CFEF").pack()

        ctk.CTkFrame(self.sidebar, height=1,
                     fg_color="#3A82C4").pack(fill="x", padx=12)

        # User card
        uc = ctk.CTkFrame(self.sidebar,fg_color="#1E293B",
                           corner_radius=RADIUS_MD)
        uc.pack(fill="x", padx=10, pady=8)
        name = self.user.get("ten_nv", "")
        initials = name[0].upper() if name else "?"
        ctk.CTkLabel(uc, text=initials,
                     width=36, height=36,
                     font=ctk.CTkFont(size=15, weight="bold"),
                     fg_color="#2563EB",
                     corner_radius=18,
                     text_color="white").pack(side="left",
                                               padx=(10, 8),
                                               pady=10)
        info = ctk.CTkFrame(uc, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, pady=10)
        ctk.CTkLabel(info, text=name,
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color="white",
                     anchor="w").pack(anchor="w")
        role = "🔑 Quản trị viên" if is_admin(self.user) else "👔 Nhân viên"
        ctk.CTkLabel(info, text=role,
                     font=ctk.CTkFont(size=FS_XS),
                     text_color="#A8CFEF",
                     anchor="w").pack(anchor="w")

        ctk.CTkFrame(self.sidebar, height=1,
                     fg_color="#3A82C4").pack(fill="x", padx=12,
                                               pady=(0, 4))

        # Menu sections
        def section(title: str):
            ctk.CTkLabel(self.sidebar, text=title,
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color="#7DBAEB").pack(
                anchor="w", padx=16, pady=(6, 2))

        def nav_btn(icon, label, key):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {label}",
                anchor="w", height=38,
                font=ctk.CTkFont(size=FS_SM),
                fg_color="transparent",
                hover_color="#172554",
                text_color="white",
                corner_radius=RADIUS_SM,
                cursor="hand2",
                command=lambda k=key: self._navigate(k))
            btn.pack(fill="x", padx=8, pady=1)
            self._nav_btns[key] = btn

        self._nav_btns = {}

        section("TỔNG QUAN")
        nav_btn("📊", "Tổng quan",       "dashboard")

        section("BÁN HÀNG")
        nav_btn("📦", "Sản phẩm",        "products")
        nav_btn("🛒", "Bán hàng (POS)",  "sales")
        nav_btn("👥", "Khách hàng",      "customers")
        nav_btn("📋", "Lịch sử hóa đơn","invoice_history")
        nav_btn("↩️",  "Trả hàng",        "returns")

        section("KHO & NHẬP HÀNG")
        nav_btn("📥", "Nhập kho",        "stock_in")
        nav_btn("🏭", "Nhà cung cấp",    "suppliers")

        section("PHÂN TÍCH")
        nav_btn("📈", "Báo cáo",         "reports")

        if is_admin(self.user):
            section("QUẢN TRỊ")
            nav_btn("👤", "Nhân viên",    "staff")
            nav_btn("⚙️",  "Cài đặt",     "settings")

        # Logout
        ctk.CTkFrame(self.sidebar, height=1,
                     fg_color="#3A82C4").pack(
            fill="x", padx=12, side="bottom", pady=(0,0))
        ctk.CTkButton(
            self.sidebar,
            text="🚪  Đăng xuất",
            anchor="w", height=38,
            font=ctk.CTkFont(size=FS_SM),
            fg_color="transparent",
            hover_color=DANGER,
            text_color="#FF8A7A",
            corner_radius=RADIUS_SM,
            cursor="hand2",
            command=self._logout,
        ).pack(fill="x", padx=8, pady=8, side="bottom")

        # ── Topbar ────────────────────────────────────────────
        self.topbar = ctk.CTkFrame(self, height=56,
                                    fg_color=CARD,
                                    corner_radius=0,
                                    border_width=0)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        self.lbl_page_title = ctk.CTkLabel(
            self.topbar, text="",
            font=ctk.CTkFont(size=FS_MD, weight="bold"),
            text_color=TEXT_PRIMARY)
        self.lbl_page_title.pack(side="left", padx=SP_LG)
        self.search_box = ctk.CTkEntry(
            self.topbar,
            placeholder_text="Tìm kiếm sản phẩm, hóa đơn...",
            width=260,
            height=36,
            corner_radius=18,
            border_width=1,
            border_color="#DCE3EA",
            fg_color="#FFFFFF",
            text_color=TEXT_PRIMARY,
            placeholder_text_color="#94A3B8",
            font=ctk.CTkFont(
                family=FONT,
                size=13
            )
        )

        self.search_box.pack(
            side="left",
            padx=(12, 0),
            pady=8
        )

        # Clock
        self.lbl_clock = ctk.CTkLabel(
            self.topbar, text="",
            font=ctk.CTkFont(size=FS_SM),
            text_color=TEXT_GRAY)
        self.lbl_clock.pack(side="right", padx=SP_LG)
        self._update_clock()

        # ── Content ───────────────────────────────────────────
        self.content = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0
        )
        self.content.pack(side="right", fill="both", expand=True)

    def _update_clock(self):
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S  |  %d/%m/%Y")
        self.lbl_clock.configure(text=now)
        self.after(1000, self._update_clock)

    def _navigate(self, key: str):
        titles = {
            "dashboard":       "📊  Tổng quan",
            "products":        "📦  Quản lý Sản phẩm",
            "sales":           "🛒  Bán hàng (POS)",
            "customers":       "👥  Quản lý Khách hàng",
            "invoice_history": "📋  Lịch sử Hóa đơn",
            "returns":         "↩️   Trả hàng & Hoàn tiền",
            "stock_in":        "📥  Nhập kho",
            "suppliers":       "🏭  Nhà cung cấp",
            "reports":         "📈  Báo cáo & Thống kê",
            "staff":           "👤  Quản lý Nhân viên",
            "settings":        "⚙️   Cài đặt hệ thống",
        }
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.configure(fg_color="#1D4ED8",
                               font=ctk.CTkFont(size=FS_SM,
                                                weight="bold"))
            else:
                btn.configure(fg_color="transparent",
                               font=ctk.CTkFont(size=FS_SM))

        self.lbl_page_title.configure(
            text=titles.get(key, ""))

        for w in self.content.winfo_children():
            w.destroy()
        try:
            if key == "dashboard":
                DashboardFrame(self.content,
                               self.user).pack(fill="both",
                                               expand=True)
            elif key == "products":
                from frontend.gui.product_ui import ProductFrame
                ProductFrame(self.content).pack(fill="both",
                                                expand=True)
            elif key == "sales":
                from frontend.gui.sales_ui import SalesFrame
                SalesFrame(self.content,
                           self.user).pack(fill="both",
                                           expand=True)
            elif key == "customers":
                from frontend.gui.customer_ui import CustomerFrame
                CustomerFrame(self.content).pack(fill="both",
                                                  expand=True)
            elif key == "invoice_history":
                from frontend.gui.invoice_history_ui import InvoiceHistoryFrame
                InvoiceHistoryFrame(self.content).pack(fill="both",
                                                        expand=True)
            elif key == "returns":
                from frontend.gui.return_ui import ReturnFrame
                ReturnFrame(self.content,
                            self.user).pack(fill="both",
                                            expand=True)
            elif key == "stock_in":
                from frontend.gui.stock_ui import StockFrame
                StockFrame(self.content,
                           self.user).pack(fill="both",
                                           expand=True)
            elif key == "suppliers":
                from frontend.gui.supplier_ui import SupplierFrame
                SupplierFrame(self.content).pack(fill="both",
                                                  expand=True)
            elif key == "reports":
                from frontend.gui.report_ui import ReportFrame
                ReportFrame(self.content).pack(fill="both",
                                               expand=True)
            elif key == "staff":
                from frontend.gui.staff_ui import StaffFrame
                StaffFrame(self.content,
                           self.user).pack(fill="both",
                                           expand=True)
            elif key == "settings":
                from frontend.gui.settings_ui import SettingsFrame
                SettingsFrame(self.content).pack(fill="both",
                                                  expand=True)
        except Exception:
            err = traceback.format_exc()
            print(f"\n[NAV ERROR] {key}:\n{err}")
            _ErrorFrame(self.content, key,
                        err).pack(fill="both", expand=True)

    def _logout(self):
        if messagebox.askyesno("Đăng xuất",
                               "Bạn có chắc muốn đăng xuất?"):
            self.destroy()


# ── Dashboard ─────────────────────────────────────────────────
class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="transparent")
        self._build(user)

    def _build(self, user):
        from datetime import datetime

        # Greeting
        hour = datetime.now().hour
        greet = ("Chào buổi sáng" if hour < 12
                 else "Chào buổi chiều" if hour < 18
                 else "Chào buổi tối")

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=SP_LG, pady=(SP_LG, SP_SM))
        ctk.CTkLabel(
            hdr, text=f"{greet}, {user['ten_nv']}! 👋",
            font=ctk.CTkFont(size=FS_2XL, weight="bold"),
            text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(
            hdr,
            text=datetime.now().strftime("%A, %d/%m/%Y"),
            font=ctk.CTkFont(size=FS_SM),
            text_color=TEXT_GRAY).pack(side="right", pady=(6, 0))

        try:
            d = get_dashboard()
        except Exception:
            d = {"so_hoa_don": 0, "doanh_thu": 0,
                 "tong_sp": 0, "sap_het": 0,
                 "tong_kh": 0, "gia_tri_kho": 0}

        # KPI Cards
        cards = [
            ("🧾", "Hóa đơn hôm nay",
             str(d.get("so_hoa_don", 0)),
             PRIMARY,  PRIMARY_LIGHT,
             "Số hóa đơn đã bán"),
            ("💰", "Doanh thu hôm nay",
             _fmt(d.get("doanh_thu", 0)),
             SUCCESS,  SUCCESS_LIGHT,
             "Tổng thanh toán hôm nay"),
            ("📦", "Sản phẩm đang bán",
             str(d.get("tong_sp", 0)),
             TEAL,     TEAL_LIGHT,
             "SP đang hoạt động"),
            ("⚠️",  "Cảnh báo tồn kho",
             str(d.get("sap_het", 0)),
             WARNING,  WARNING_LIGHT,
             "SP cần đặt hàng thêm"),
            ("👥", "Khách hàng",
             str(d.get("tong_kh", 0)),
             PURPLE,   PURPLE_LIGHT,
             "Tổng số khách hàng"),
            ("🏪", "Giá trị kho",
             _fmt(d.get("gia_tri_kho", 0)),
             DANGER,   DANGER_LIGHT,
             "Tổng giá trị tồn kho"),
        ]

        card_row = ctk.CTkFrame(self, fg_color="transparent")
        card_row.pack(fill="x", padx=SP_MD, pady=(0, SP_MD))
        for i, (icon, title, val, color, bg, sub) in enumerate(cards):
            self._kpi(
                card_row,
                icon,
                title,
                val,
                color,
                bg,
                sub
            )

        for i in range(3):
            card_row.grid_columnconfigure(i, weight=1)

        # Bottom 2 cột
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="both", expand=True,
                 padx=SP_MD, pady=(0, SP_MD))
        self._quick_actions(bot)
        self._alerts(bot, d)

    def _kpi(self, parent, icon, title, val, color, bg, sub):

        # Shadow giả
        outer = ctk.CTkFrame(
            parent,
            fg_color="#E2E8F0",
            corner_radius=18
        )

        outer.pack(
            side="left",
            fill="x",
            expand=True,
            padx=6,
            pady=4
        )

        # Card thật
        f = ctk.CTkFrame(
            outer,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color="#E5E7EB"
        )

        f.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=(0, 1)
        )

        # Accent line
        ctk.CTkFrame(
            f,
            fg_color=color,
            height=4,
            corner_radius=0
        ).pack(fill="x")

        body = ctk.CTkFrame(
            f,
            fg_color="transparent"
        )

        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=18
        )

        # Top row
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x")

        # Icon
        icon_box = ctk.CTkFrame(
            top,
            width=48,
            height=48,
            fg_color=bg,
            corner_radius=14
        )

        icon_box.pack(side="left")
        icon_box.pack_propagate(False)

        ctk.CTkLabel(
            icon_box,
            text=icon,
            font=ctk.CTkFont(size=24)
        ).pack(expand=True)

        # Text content
        txt = ctk.CTkFrame(top, fg_color="transparent")
        txt.pack(side="left", padx=14, fill="both", expand=True)

        ctk.CTkLabel(
            txt,
            text=title,
            anchor="w",
            font=ctk.CTkFont(
                family=FONT_BOLD,
                size=13
            ),
            text_color=TEXT_SECOND
        ).pack(anchor="w")

        ctk.CTkLabel(
            txt,
            text=val,
            anchor="w",
            font=ctk.CTkFont(
                family=FONT_BOLD,
                size=30,
                weight="bold"
            ),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            txt,
            text=sub,
            anchor="w",
            font=ctk.CTkFont(
                family=FONT,
                size=12
            ),
            text_color=TEXT_GRAY
        ).pack(anchor="w", pady=(4, 0))

    def _quick_actions(self, parent):
        frm = make_card(parent)
        frm.pack(side="left", fill="both", expand=True,
                 padx=(0, SP_SM))

        ctk.CTkLabel(
            frm,
            text="⚡  Thao tác nhanh",
            font=ctk.CTkFont(size=FS_LG, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=SP_MD, pady=(SP_MD, SP_SM))

        divider(frm).pack(fill="x", padx=SP_MD)

        actions = [
            ("🛒", "Bán hàng", PRIMARY, "sales"),
            ("📦", "Thêm sản phẩm", SUCCESS, "products"),
            ("📥", "Nhập kho", WARNING, "stock_in"),
            ("📋", "Lịch sử HĐ", TEAL, "invoice_history"),
            ("↩️", "Trả hàng", DANGER, "returns"),
            ("📈", "Xem báo cáo", PURPLE, "reports"),
        ]

        grid = ctk.CTkFrame(frm, fg_color="transparent")
        grid.pack(fill="both", expand=True,
                  padx=SP_MD, pady=SP_MD)

        for i, (icon, label, color, page) in enumerate(actions):
            btn = ctk.CTkButton(
                grid,
                text=f"{icon}  {label}",
                font=ctk.CTkFont(size=13, family=FONT_BOLD),
                fg_color=color,
                hover_color=color,
                text_color="white",
                height=88,
                corner_radius=16,
                cursor="hand2",
                border_width=1,
                border_color="#FFFFFF",

                # FIX CHÍNH
                command=lambda p=page: self.master.master._navigate(p)
            )

            btn.grid(
                row=i // 3,
                column=i % 3,
                padx=4,
                pady=4,
                sticky="nsew"
            )

        for col in range(3):
            grid.columnconfigure(col, weight=1)

    def _alerts(self, parent, d):
        frm = make_card(parent)
        frm.configure(width=300)
        frm.pack(side="right", fill="y")
        frm.pack_propagate(False)

        ctk.CTkLabel(frm, text="🔔  Thông báo",
                     font=ctk.CTkFont(size=FS_LG, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=SP_MD, pady=(SP_MD, SP_SM))
        divider(frm).pack(fill="x", padx=SP_MD)

        alerts = []
        if d.get("sap_het", 0) > 0:
            alerts.append((WARNING, "⚠️",
                           f"{d['sap_het']} sản phẩm sắp hết hàng",
                           "Cần đặt thêm ngay!"))
        if d.get("so_hoa_don", 0) == 0:
            alerts.append((TEAL, "💡",
                           "Chưa có hóa đơn hôm nay",
                           "Bắt đầu ngày làm việc!"))
        if not alerts:
            alerts.append((SUCCESS, "✅",
                           "Mọi thứ ổn định",
                           "Không có cảnh báo hôm nay"))

        for color, icon, title, sub in alerts:
            item = ctk.CTkFrame(
                frm,
                fg_color=CARD,
                corner_radius=RADIUS_SM,
                border_width=0,
                border_color=color
            )
            item.pack(fill="x", padx=SP_MD, pady=4)
            r = ctk.CTkFrame(item, fg_color="transparent")
            r.pack(fill="x", padx=SP_SM, pady=SP_SM)
            ctk.CTkLabel(r, text=icon,
                         font=ctk.CTkFont(size=20),
                         width=28).pack(side="left")
            txt = ctk.CTkFrame(r, fg_color="transparent")
            txt.pack(side="left", padx=6, fill="x")
            ctk.CTkLabel(txt, text=title, anchor="w",
                         font=ctk.CTkFont(size=FS_SM,
                                          weight="bold"),
                         text_color=color).pack(anchor="w")
            ctk.CTkLabel(txt, text=sub, anchor="w",
                         font=ctk.CTkFont(size=FS_XS),
                         text_color=TEXT_GRAY).pack(anchor="w")


def _fmt(val: float) -> str:
    val = float(val or 0)
    if val >= 1_000_000:
        return f"{val/1_000_000:.1f}M đ"
    if val >= 1_000:
        return f"{val/1_000:.0f}K đ"
    return f"{val:,.0f}đ"


# ── Error Frame ───────────────────────────────────────────────
class _ErrorFrame(ctk.CTkFrame):
    def __init__(self, parent, key, err):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self,
                     text=f"⚠️  Lỗi tải: {key}",
                     font=ctk.CTkFont(size=FS_LG, weight="bold"),
                     text_color=DANGER).pack(pady=(40, SP_MD))
        box = ctk.CTkTextbox(
            self, height=220,
            font=ctk.CTkFont(size=FS_XS, family="Courier New"))
        box.pack(fill="x", padx=60)
        box.insert("1.0", err)
        box.configure(state="disabled")


# missing imports
TEAL = "#0E7490"; TEAL_LIGHT = "#CFFAFE"
