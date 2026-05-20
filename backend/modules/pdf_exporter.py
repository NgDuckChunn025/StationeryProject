# backend/modules/pdf_exporter.py — fix dùng config thay vì hardcode
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(
    TTFont("Arial", "C:/Windows/Fonts/arial.ttf")
)

pdfmetrics.registerFont(
    TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf")
)


def _store():
    """Lấy thông tin cửa hàng từ DB hoặc fallback mặc định."""
    try:
        from backend.modules.config_service import get_store_info
        return get_store_info()
    except Exception:
        return {"ten_cua_hang": "Cửa Hàng VPP",
                "dia_chi": "", "so_dien_thoai": "", "email": "", "website": ""}


def export_invoice(ma_hd: int, ten_kh: str, ten_nv: str,
                   items: list, tong_tien: float, giam_gia: float,
                   filepath: str, hinh_thuc: str = "Tiền mặt") -> bool:
    """
    Xuất hóa đơn PDF (A5).
    items = [(ten_sp, don_gia, so_luong, thanh_tien), ...]
    """
    try:
        info = _store()
        doc = SimpleDocTemplate(
            filepath, pagesize=A5,
            leftMargin=1.5*cm, rightMargin=1.5*cm,
            topMargin=1.5*cm,  bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        body   = []

        # ── Header cửa hàng ──────────────────────────────────
        st_h1 = ParagraphStyle("h1", parent=styles["Title"],
                                fontSize=15, spaceAfter=3, leading=19, fontName="Arial-Bold",)
        st_sub = ParagraphStyle("sub", parent=styles["Normal"],
                                 fontSize=9, fontName="Arial",
                                 textColor=colors.HexColor("#555555"))

        body.append(Paragraph(info["ten_cua_hang"], st_h1))

        contact_parts = []
        if info["dia_chi"]:
            contact_parts.append(info["dia_chi"])
        if info["so_dien_thoai"]:
            contact_parts.append(f"ĐT: {info['so_dien_thoai']}")
        if info["email"]:
            contact_parts.append(info["email"])
        if contact_parts:
            body.append(Paragraph("  |  ".join(contact_parts), st_sub))
        body.append(Spacer(1, 0.25*cm))

        # ── Tiêu đề hóa đơn ───────────────────────────────────
        body.append(Paragraph(
            f"<b>HÓA ĐƠN BÁN HÀNG</b>   #{ma_hd:04d}",
            ParagraphStyle("hd", parent=styles["Heading2"], fontSize=13, fontName="Arial-Bold",)))
        body.append(Paragraph(
            f"Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')}   "
            f"Khách: <b>{ten_kh}</b>   NV: {ten_nv}   "
            f"TT: {hinh_thuc}", st_sub))
        body.append(Spacer(1, 0.25*cm))

        # ── Bảng chi tiết ─────────────────────────────────────
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
            ["", "", "TỔNG:",  f"{tong_tien:,.0f}đ"],
            ["", "", "Giảm:", f"-{giam_gia:,.0f}đ"],
            ["", "", "TRẢ:",   f"{thanh_toan:,.0f}đ"],
        ]

        tbl = Table(tbl_data, colWidths=[6.5*cm, 2.5*cm, 1.2*cm, 2.8*cm])
        tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 1), (-1, -1), "Arial"),
            ("BACKGROUND",    (0, 0),  (-1, 0),   colors.HexColor("#1565C0")),
            ("TEXTCOLOR",     (0, 0),  (-1, 0),   colors.white),
            ("FONTNAME",      (0, 0),  (-1, 0),   "Arial-Bold"),
            ("FONTSIZE",      (0, 0),  (-1, -1),  9),
            ("ALIGN",         (1, 0),  (-1, -1),  "RIGHT"),
            ("ROWBACKGROUNDS",(0, 1),  (-1, -4),
             [colors.white, colors.HexColor("#EAF2FF")]),
            ("GRID",          (0, 0),  (-1, -4),  0.4,
             colors.HexColor("#BBBBBB")),
            ("LINEABOVE",     (0, -3), (-1, -3),  1, colors.black),
            ("FONTNAME",      (2, -3), (-1, -1),  "Arial-Bold"),
            ("TEXTCOLOR",     (2, -1), (-1, -1),  colors.HexColor("#1565C0")),
            ("FONTSIZE",      (2, -1), (-1, -1),  10),
            ("TOPPADDING",    (0, 0),  (-1, -1),  4),
            ("BOTTOMPADDING", (0, 0),  (-1, -1),  4),
        ]))
        body.append(tbl)
        body.append(Spacer(1, 0.4*cm))
        body.append(Paragraph(
            "Cảm ơn quý khách! Hẹn gặp lại",
            ParagraphStyle(
                "thanks",
                parent=styles["Normal"],
                fontName="Arial",
                alignment=1,
                fontSize=10,
                textColor=colors.HexColor("#1565C0")
            )
        ))
        doc.build(body)
        return True
    except Exception as e:
        print(f"Lỗi xuất PDF: {e}")
        return False


def export_return_slip(ma_phieu: int, ten_kh: str, ten_nv: str,
                       items: list, tong_hoan: float, ly_do: str,
                       filepath: str) -> bool:
    """Xuất phiếu trả hàng PDF."""
    try:
        info = _store()
        doc = SimpleDocTemplate(
            filepath, pagesize=A5,
            leftMargin=1.5*cm, rightMargin=1.5*cm,
            topMargin=1.5*cm,  bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        body   = []

        st_h1  = ParagraphStyle("h1", parent=styles["Title"],
                                 fontSize=15, spaceAfter=3, leading=19)
        st_sub = ParagraphStyle("sub", parent=styles["Normal"],
                                 fontSize=9,
                                 textColor=colors.HexColor("#555555"))

        body.append(Paragraph(info["ten_cua_hang"], st_h1))
        body.append(Paragraph(
            f"<b>PHIẾU TRẢ HÀNG</b>   #{ma_phieu:04d}",
            ParagraphStyle("hd", parent=styles["Heading2"],
                           fontSize=13,
                           textColor=colors.HexColor("#BA3325"))))
        body.append(Paragraph(
            f"Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')}   "
            f"Khách: <b>{ten_kh}</b>   NV: {ten_nv}", st_sub))
        if ly_do:
            body.append(Paragraph(f"Lý do: {ly_do}", st_sub))
        body.append(Spacer(1, 0.25*cm))

        tbl_data = [["Tên sản phẩm", "Đơn giá", "SL trả", "Hoàn tiền"]]
        for ten_sp, don_gia, sl_tra, hoan in items:
            tbl_data.append([
                ten_sp,
                f"{float(don_gia):,.0f}đ",
                str(sl_tra),
                f"{float(hoan):,.0f}đ",
            ])
        tbl_data.append(["", "", "TỔNG HOÀN:", f"{tong_hoan:,.0f}đ"])

        tbl = Table(tbl_data, colWidths=[6.5*cm, 2.5*cm, 1.2*cm, 2.8*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0),  (-1, 0),
             colors.HexColor("#BA3325")),
            ("TEXTCOLOR",     (0, 0),  (-1, 0),   colors.white),
            ("FONTNAME",      (0, 0),  (-1, 0),   "Arial-Bold"),
            ("FONTSIZE",      (0, 0),  (-1, -1),  9),
            ("ALIGN",         (1, 0),  (-1, -1),  "RIGHT"),
            ("ROWBACKGROUNDS",(0, 1),  (-1, -2),
             [colors.white, colors.HexColor("#FDECEB")]),
            ("GRID",          (0, 0),  (-1, -2),  0.4,
             colors.HexColor("#BBBBBB")),
            ("FONTNAME",      (2, -1), (-1, -1),  "HArial-Bold"),
            ("TEXTCOLOR",     (2, -1), (-1, -1),
             colors.HexColor("#BA3325")),
            ("FONTSIZE",      (2, -1), (-1, -1),  10),
            ("TOPPADDING",    (0, 0),  (-1, -1),  4),
            ("BOTTOMPADDING", (0, 0),  (-1, -1),  4),
        ]))
        body.append(tbl)
        doc.build(body)
        return True
    except Exception as e:
        print(f"Lỗi xuất phiếu trả: {e}")
        return False
