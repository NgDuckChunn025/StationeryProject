# frontend/gui/report_ui.py

import customtkinter as ctk
from tkinter import ttk
from backend.modules.report_service import get_dashboard


class ReportFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()

    def _build(self):
        # ===== TITLE =====
        ctk.CTkLabel(
            self,
            text="BÁO CÁO VÀ THỐNG KÊ",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            self,
            text="Tổng quan doanh thu và hiệu suất bán hàng",
            text_color="gray"
        ).pack(anchor="w", padx=20, pady=(0, 14))

        # ===== BUTTONS =====
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=20, pady=10)

        for text in ["Xem", "Xuất Excel", "Biểu đồ"]:
            ctk.CTkButton(
                btn_frame,
                text=text,
                width=120,
                height=36,
                corner_radius=10
            ).pack(side="left", padx=8)

        # ===== SUMMARY =====
        try:
            data = get_dashboard()
        except:
            data = {
                "doanh_thu": 0,
                "so_hoa_don": 0,
                "tong_sp": 0,
                "sap_het": 0
            }

        box_frame = ctk.CTkFrame(self, fg_color="transparent")
        box_frame.pack(padx=20, pady=10)

        boxes = [
            ("Doanh thu", f"{data['doanh_thu']:,.0f}đ"),
            ("Hóa đơn", data["so_hoa_don"]),
            ("SP bán", data["tong_sp"]),
            ("Sắp hết", data["sap_het"]),
        ]

        for title, val in boxes:
            card = ctk.CTkFrame(
                box_frame,
                width=150,
                height=80,
                corner_radius=12,
                fg_color="white"
            )
            card.pack(side="left", padx=10)
            card.pack_propagate(False)

            ctk.CTkLabel(card, text=title, text_color="gray").pack(pady=(10, 0))
            ctk.CTkLabel(
                card,
                text=str(val),
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack()

        # ===== TABLE DOANH THU =====
        ctk.CTkLabel(
            self,
            text="DOANH THU THEO NGÀY",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 6))

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Ngày", "Số hóa đơn", "Doanh thu")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # demo data (cho đẹp UI)
        demo = [
            ("2025-05-01", 12, "2,500,000"),
            ("2025-05-02", 8, "1,800,000"),
            ("2025-05-03", 15, "3,200,000"),
        ]

        for row in demo:
            self.tree.insert("", "end", values=row)