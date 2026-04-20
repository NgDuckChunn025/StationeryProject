# backend/modules/pdf_exporter.py
# ================================================================
# Xuất hóa đơn PDF bằng reportlab
# ================================================================

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime


def export_invoice(ma_hd: int, ten_kh: str, ten_nv: str,
                   items: list, tong_tien: float, giam_gia: float,
                   filepath: str) -> bool:
    """
    Xuất hóa đơn ra file PDF (khổ A5).

    items = [(ten_sp, don_gia, so_luong, thanh_tien), ...]
    """
    try:
        doc = SimpleDocTemplate(
            filepath, pagesize=A5,
            leftMargin=1.5*cm, rightMargin=1.5*cm,
            topMargin=1.5*cm, bottomMargin=1.5*cm
        )
        styles = getSampleStyleSheet()
        body = []

        # ---- Header ----
        style_h1 = ParagraphStyle("h1", parent=styles["Title"],
                                   fontSize=16, spaceAfter=4, leading=20)
        style_sub = ParagraphStyle("sub", parent=styles["Normal"],
                                    fontSize=10, textColor=colors.HexColor("#555555"))

        body.append(Paragraph("🛒 CỬA HÀNG VĂN PHÒNG PHẨM", style_h1))
        body.append(Paragraph("123 Đường ABC, Q.1, TP.HCM  |  ĐT: 028 xxxx xxxx", style_sub))
        body.append(Spacer(1, 0.3*cm))

        body.append(Paragraph(
            f"<b>HÓA ĐƠN BÁN HÀNG</b> &nbsp;&nbsp; #{ma_hd:04d}",
            ParagraphStyle("hd_title", parent=styles["Heading2"], fontSize=13)
        ))
        body.append(Paragraph(
            f"Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')} &nbsp;&nbsp; "
            f"Khách: <b>{ten_kh}</b> &nbsp;&nbsp; NV: {ten_nv}",
            style_sub
        ))
        body.append(Spacer(1, 0.3*cm))

        # ---- Bảng chi tiết ----
        tbl_data = [["Tên sản phẩm", "Đơn giá", "SL", "Thành tiền"]]
        for ten_sp, don_gia, so_luong, thanh_tien in items:
            tbl_data.append([
                ten_sp,
                f"{float(don_gia):,.0f}đ",
                str(so_luong),
                f"{float(thanh_tien):,.0f}đ",
            ])

        thanh_toan = tong_tien - giam_gia
        tbl_data += [
            ["", "", "TỔNG:",    f"{tong_tien:,.0f}đ"],
            ["", "", "Giảm:",    f"-{giam_gia:,.0f}đ"],
            ["", "", "Trả:",     f"{thanh_toan:,.0f}đ"],
        ]

        tbl = Table(tbl_data, colWidths=[6.5*cm, 2.5*cm, 1.2*cm, 2.8*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0),  (-1, 0),   colors.HexColor("#1565C0")),
            ("TEXTCOLOR",     (0, 0),  (-1, 0),   colors.white),
            ("FONTNAME",      (0, 0),  (-1, 0),   "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0),  (-1, -1),  9),
            ("ALIGN",         (1, 0),  (-1, -1),  "RIGHT"),
            ("ROWBACKGROUNDS",(0, 1),  (-1, -4),  [colors.white, colors.HexColor("#E3F2FD")]),
            ("GRID",          (0, 0),  (-1, -4),  0.4, colors.HexColor("#BBBBBB")),
            ("LINEABOVE",     (0, -3), (-1, -3),  1, colors.black),
            ("FONTNAME",      (2, -3), (-1, -1),  "Helvetica-Bold"),
            ("TEXTCOLOR",     (2, -1), (-1, -1),  colors.HexColor("#1565C0")),
            ("FONTSIZE",      (2, -1), (-1, -1),  10),
        ]))
        body.append(tbl)
        body.append(Spacer(1, 0.5*cm))
        body.append(Paragraph(
            "Cảm ơn quý khách! Hẹn gặp lại",
            ParagraphStyle("thanks", parent=styles["Normal"],
                           alignment=1, fontSize=10,
                           textColor=colors.HexColor("#1565C0"))
        ))

        doc.build(body)
        return True
    except Exception as e:
        print(f"Lỗi xuất PDF: {e}")
        return False