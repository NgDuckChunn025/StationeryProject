import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta

from backend.modules.auth_service import is_admin
from backend.modules.report_service import get_dashboard, revenue_by_day, plot_revenue
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self, user: dict):
        super().__init__()
        ctk.set_appearance_mode("light")  # hoặc "dark"
        ctk.set_default_color_theme("blue")

        # Font global
        default_font = ctk.CTkFont(family="Segoe UI", size=13)
        self.option_add("*Font", "SegoeUI 11")
        self.user = user
        self.title("VPP Manager — Quản lý cửa hàng")
        self.geometry("1300x740")
        self.minsize(1100, 650)
        self.eval("tk::PlaceWindow . center")

        self._build_ui()
        self._navigate("dashboard")

    # ================= UI =================
    def _build_ui(self):
        # ===== Sidebar =====
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color="#0D47A1")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="VPP Manager",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self.sidebar,
            text=f"{self.user['ten_nv']} ({self.user['vai_tro']})",
            font=ctk.CTkFont(size=12),
            text_color="#BBDEFB"
        ).pack(pady=(0, 20))

        menu = [
            ("Tổng quan", "dashboard"),
            ("Sản phẩm", "products"),
            ("Bán hàng", "sales"),
            ("Khách hàng", "customers"),
            ("Nhập kho", "stock_in"),
            ("Báo cáo", "reports"),
        ]

        if is_admin(self.user):
            menu.append(("Nhân viên", "staff"))

        self._nav_btns = {}

        for label, key in menu:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=44,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color="#1565C0",
                text_color="white",
                corner_radius=10,
                command=lambda k=key: self._navigate(k)
            )
            btn.pack(fill="x", padx=10, pady=3)
            self._nav_btns[key] = btn

        ctk.CTkButton(
            self.sidebar,
            text="Đăng xuất",
            height=44,
            fg_color="transparent",
            hover_color="#C62828",
            text_color="white",
            command=self._logout
        ).pack(fill="x", padx=10, pady=10, side="bottom")

        # ===== Content =====
        self.content = ctk.CTkFrame(self, fg_color="#F8FAFC")
        self.content.pack(side="right", fill="both", expand=True)

    # ================= NAV =================
    def _navigate(self, key):
        for k, btn in self._nav_btns.items():
            btn.configure(fg_color="#1565C0" if k == key else "transparent")

        for w in self.content.winfo_children():
            w.destroy()

        if key == "dashboard":
            DashboardFrame(self.content, self.user).pack(fill="both", expand=True)

        elif key == "products":
            from frontend.gui.product_ui import ProductFrame
            ProductFrame(self.content).pack(fill="both", expand=True)

        elif key == "sales":
            from frontend.gui.sales_ui import SalesFrame
            SalesFrame(self.content, self.user).pack(fill="both", expand=True)

        elif key == "customers":
            from frontend.gui.customer_ui import CustomerFrame
            CustomerFrame(self.content).pack(fill="both", expand=True)

        elif key == "reports":
            from frontend.gui.report_ui import ReportFrame
            ReportFrame(self.content).pack(fill="both", expand=True)

        elif key == "staff":
            from frontend.gui.staff_ui import StaffFrame
            StaffFrame(self.content).pack(fill="both", expand=True)

        elif key == "stock_in":
            from frontend.gui.stock_ui import StockFrame
            #  FIX QUAN TRỌNG: truyền user vào đây
            StockFrame(self.content, self.user).pack(fill="both", expand=True)

        else:
            _PlaceholderFrame(self.content, key).pack(fill="both", expand=True)

    def _logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            self.destroy()


# ================= DASHBOARD =================
class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="transparent")
        self._build(user)

    def _build(self, user):
        ctk.CTkLabel(
            self,
            text=f"Xin chào, {user['ten_nv']}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            self,
            text="Tổng quan hoạt động cửa hàng",
            text_color="gray"
        ).pack(anchor="w", padx=24, pady=(0, 18))

        # ===== Chart =====
        try:
            tu = str(date.today() - timedelta(days=6))
            den = str(date.today())
            data = revenue_by_day(tu, den)

            fig = plot_revenue(data)
            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", padx=20, pady=10)

        except Exception as e:
            print("Chart lỗi:", e)

        # ===== Data =====
        try:
            data = get_dashboard()
        except:
            data = {"so_hoa_don": 0, "doanh_thu": 0, "tong_sp": 0, "sap_het": 0, "tong_kh": 0}

        cards = [
            ("Hóa đơn", data["so_hoa_don"], "#1976D2"),
            ("Doanh thu", f"{data['doanh_thu']:,.0f}đ", "#2E7D32"),
            ("Sản phẩm", data["tong_sp"], "#FB8C00"),
            ("Sắp hết", data["sap_het"], "#E53935"),
            ("Khách", data["tong_kh"], "#8E24AA"),
        ]

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=10)

        for title, val, color in cards:
            card = ctk.CTkFrame(
                row,
                fg_color="white",
                corner_radius=14,
                border_width=1,
                border_color="#E5E7EB"
            )
            card.pack(side="left", fill="both", expand=True, padx=8)

            ctk.CTkLabel(card, text=title,
                         text_color="gray",
                         font=ctk.CTkFont(size=13)).pack(anchor="w", padx=14, pady=(14, 4))

            ctk.CTkLabel(card, text=str(val),
                         text_color=color,
                         font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=14, pady=(0, 14))


class _PlaceholderFrame(ctk.CTkFrame):
    def __init__(self, parent, key):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(
            self,
            text=f"{key} đang phát triển...",
            text_color="gray",
            font=ctk.CTkFont(size=16)
        ).pack(expand=True)