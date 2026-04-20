# backend/modules/report_service.py
# ================================================================
# Thống kê, báo cáo & xuất Excel (openpyxl), biểu đồ (matplotlib)
# ================================================================

from backend.database.connection import get_connection


def get_dashboard() -> dict:
    """Số liệu tổng quan cho màn hình Tổng quan."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*), COALESCE(SUM(thanh_toan), 0)
        FROM hoa_don WHERE DATE(ngay_ban) = CURDATE()
    """)
    so_hd, doanh_thu = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM san_pham WHERE trang_thai=1")
    tong_sp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM san_pham WHERE ton_kho<=10 AND trang_thai=1")
    sap_het = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM khach_hang")
    tong_kh = cursor.fetchone()[0]

    conn.close()
    return {
        "so_hoa_don" : int(so_hd),
        "doanh_thu"  : float(doanh_thu),
        "tong_sp"    : int(tong_sp),
        "sap_het"    : int(sap_het),
        "tong_kh"    : int(tong_kh),
    }


def revenue_by_day(tu_ngay: str, den_ngay: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(ngay_ban), COUNT(*), SUM(thanh_toan)
        FROM hoa_don
        WHERE DATE(ngay_ban) BETWEEN %s AND %s
        GROUP BY DATE(ngay_ban)
        ORDER BY DATE(ngay_ban)
    """, (tu_ngay, den_ngay))
    result = cursor.fetchall()
    conn.close()
    return result


def top_products(limit=10) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sp.ten_sp,
               SUM(ct.so_luong) AS tong_ban,
               SUM(ct.don_gia * ct.so_luong) AS doanh_thu
        FROM chi_tiet_hoa_don ct
        JOIN san_pham sp ON ct.ma_sp = sp.ma_sp
        GROUP BY sp.ten_sp
        ORDER BY tong_ban DESC
        LIMIT %s
    """, (limit,))
    result = cursor.fetchall()
    conn.close()
    return result


# ---- Xuất Excel với openpyxl ----
def export_excel(data: list, filepath: str) -> bool:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter

        wb = Workbook()
        ws = wb.active
        ws.title = "Doanh thu"

        headers = ["Ngày", "Số hóa đơn", "Doanh thu (đ)"]
        fill = PatternFill("solid", fgColor="1565C0")
        for col, h in enumerate(headers, 1):
            c = ws.cell(row=1, column=col, value=h)
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = fill
            c.alignment = Alignment(horizontal="center")

        tong = 0
        for i, (ngay, so_hd, dt) in enumerate(data, 2):
            ws.cell(row=i, column=1, value=str(ngay))
            ws.cell(row=i, column=2, value=int(so_hd))
            dt_f = float(dt or 0)
            ws.cell(row=i, column=3, value=dt_f)
            tong += dt_f

        # Dòng tổng
        r = len(data) + 2
        ws.cell(row=r, column=2, value="TỔNG").font = Font(bold=True)
        ws.cell(row=r, column=3, value=tong).font = Font(bold=True)

        for col in range(1, 4):
            ws.column_dimensions[get_column_letter(col)].width = 22

        wb.save(filepath)
        return True
    except Exception as e:
        print(f"Lỗi xuất Excel: {e}")
        return False


# ---- Biểu đồ matplotlib ----
def plot_revenue(data: list):
    """Trả về matplotlib Figure để nhúng vào GUI."""
    import matplotlib.pyplot as plt

    ngay = [str(r[0]) for r in data]
    dt   = [float(r[2] or 0) for r in data]

    fig, ax = plt.subplots(figsize=(8, 3.5))
    bars = ax.bar(ngay, dt, color="#1565C0", alpha=0.85, width=0.6)
    ax.set_title("Doanh thu theo ngày", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel("Doanh thu (đ)")
    ax.tick_params(axis="x", rotation=35, labelsize=9)
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x/1_000_000:.1f}M" if x >= 1e6 else f"{x:,.0f}")
    )
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    return fig