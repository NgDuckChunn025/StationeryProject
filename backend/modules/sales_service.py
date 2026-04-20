# backend/modules/sales_service.py
# ================================================================
# Nghiệp vụ bán hàng: tạo hóa đơn, cập nhật tồn kho (transaction)
# ================================================================

from backend.database.connection import get_connection
from backend.models.invoice import Invoice


# ================================================================
# TẠO HÓA ĐƠN
# ================================================================
def create_invoice(invoice: Invoice) -> tuple[bool, int | str]:
    if not invoice.items:
        return False, "Hóa đơn trống!"

    d = invoice.to_dict()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ========================================================
        # 1. CHECK TỒN KHO TRƯỚC (QUAN TRỌNG)
        # ========================================================
        for item in d["items"]:
            cursor.execute("""
                SELECT ton_kho, ten_sp
                FROM san_pham
                WHERE ma_sp = %s
            """, (item["ma_sp"],))
            row = cursor.fetchone()

            if not row:
                raise Exception(f"Sản phẩm #{item['ma_sp']} không tồn tại!")

            ton_kho, ten_sp = row

            if ton_kho < item["so_luong"]:
                raise Exception(f"{ten_sp} không đủ hàng (còn {ton_kho})")

        # ========================================================
        # 2. TẠO HÓA ĐƠN
        # ========================================================
        cursor.execute("""
            INSERT INTO hoa_don (
                ma_kh, ma_nv, tong_tien, giam_gia, thanh_toan, hinh_thuc
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            d["ma_kh"],
            d["ma_nv"],
            d["tong_tien"],
            d["giam_gia"],
            d["thanh_toan"],
            d["hinh_thuc"]
        ))

        ma_hd = cursor.lastrowid

        # ========================================================
        # 3. THÊM CHI TIẾT + TRỪ KHO
        # ========================================================
        for item in d["items"]:
            # Chi tiết hóa đơn
            cursor.execute("""
                INSERT INTO chi_tiet_hoa_don (
                    ma_hd, ma_sp, so_luong, don_gia
                )
                VALUES (%s,%s,%s,%s)
            """, (
                ma_hd,
                item["ma_sp"],
                item["so_luong"],
                item["don_gia"]
            ))

            # Trừ tồn kho
            cursor.execute("""
                UPDATE san_pham
                SET ton_kho = ton_kho - %s
                WHERE ma_sp = %s
            """, (
                item["so_luong"],
                item["ma_sp"]
            ))

        # ========================================================
        # 4. COMMIT
        # ========================================================
        conn.commit()
        return True, ma_hd

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        conn.close()


# ================================================================
# DANH SÁCH HÓA ĐƠN
# ================================================================
def get_invoices(tu_ngay=None, den_ngay=None) -> list:
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT hd.ma_hd,
               COALESCE(kh.ten_kh, 'Khách lẻ') AS ten_kh,
               nv.ten_nv,
               hd.ngay_ban,
               hd.tong_tien,
               hd.giam_gia,
               hd.thanh_toan,
               hd.hinh_thuc
        FROM hoa_don hd
        LEFT JOIN khach_hang kh ON hd.ma_kh = kh.ma_kh
        LEFT JOIN nhan_vien nv ON hd.ma_nv = nv.ma_nv
    """

    params = []

    if tu_ngay and den_ngay:
        sql += " WHERE DATE(hd.ngay_ban) BETWEEN %s AND %s"
        params = [tu_ngay, den_ngay]

    sql += " ORDER BY hd.ngay_ban DESC"

    cursor.execute(sql, params)
    result = cursor.fetchall()
    conn.close()
    return result


# ================================================================
# CHI TIẾT HÓA ĐƠN
# ================================================================
def get_invoice_detail(ma_hd: int) -> list:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sp.ten_sp,
               ct.don_gia,
               ct.so_luong,
               (ct.don_gia * ct.so_luong) AS thanh_tien
        FROM chi_tiet_hoa_don ct
        JOIN san_pham sp ON ct.ma_sp = sp.ma_sp
        WHERE ct.ma_hd = %s
    """, (ma_hd,))

    result = cursor.fetchall()
    conn.close()
    return result


# ================================================================
# KHÁCH HÀNG (CHO POS)
# ================================================================
def get_customers() -> list:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ma_kh, ten_kh, so_dt
        FROM khach_hang
        ORDER BY ten_kh
    """)

    result = cursor.fetchall()
    conn.close()
    return result