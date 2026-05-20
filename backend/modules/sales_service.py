# backend/modules/sales_service.py
# ================================================================
# SalesService — tạo hóa đơn, truy vấn lịch sử bán hàng
# ================================================================

from backend.database.connection import get_connection
from backend.models.invoice import Invoice


class SalesService:
    """Lớp service quản lý nghiệp vụ bán hàng."""

    def _date_col(self) -> str:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COLUMN_NAME FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'hoa_don'
              AND COLUMN_NAME IN ('ngay_ban','created_at','ngay_tao')
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "ngay_ban"

    def create_invoice(self, invoice: Invoice) -> tuple[bool, int | str]:
        """
        Lưu hóa đơn và trừ tồn kho trong một transaction.
        Trả về (True, ma_hd) hoặc (False, thông báo lỗi).
        """
        if not invoice.items:
            return False, "Hóa đơn trống!"
        d = invoice.to_dict()
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO hoa_don
                    (ma_kh, ma_nv, tong_tien, giam_gia, thanh_toan, hinh_thuc)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (d["ma_kh"], d["ma_nv"], d["tong_tien"],
                  d["giam_gia"], d["thanh_toan"], d["hinh_thuc"]))
            ma_hd = cursor.lastrowid

            for item in d["items"]:
                cursor.execute("""
                    INSERT INTO chi_tiet_hoa_don (ma_hd, ma_sp, so_luong, don_gia)
                    VALUES (%s, %s, %s, %s)
                """, (ma_hd, item["ma_sp"], item["so_luong"], item["don_gia"]))
                cursor.execute("""
                    UPDATE san_pham SET ton_kho = ton_kho - %s
                    WHERE ma_sp = %s AND ton_kho >= %s
                """, (item["so_luong"], item["ma_sp"], item["so_luong"]))
                if cursor.rowcount == 0:
                    raise Exception(
                        f"Sản phẩm #{item['ma_sp']} không đủ số lượng trong kho!")

            conn.commit()

            # cập nhật điểm + chi tiêu + hạng KH
            try:
                if d["ma_kh"]:
                    from backend.modules.customer_service import cap_nhat_sau_mua

                    cap_nhat_sau_mua(
                        ma_kh=d["ma_kh"],
                        so_tien=d["thanh_toan"],
                        so_diem_tru=0
                    )
            except Exception as e:
                print(f"[CUSTOMER UPDATE] {e}")

            return True, ma_hd
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def get_invoices(self, tu_ngay=None, den_ngay=None) -> list:
        """Lấy danh sách hóa đơn, có thể lọc theo khoảng ngày."""
        dc = self._date_col()
        conn = get_connection()
        cursor = conn.cursor()
        sql = f"""
            SELECT hd.ma_hd,
                   COALESCE(kh.ten_kh, 'Khách lẻ'),
                   COALESCE(nv.ten_nv, '—'),
                   hd.{dc}, hd.tong_tien, hd.giam_gia, hd.thanh_toan, hd.hinh_thuc
            FROM hoa_don hd
            LEFT JOIN khach_hang kh ON hd.ma_kh = kh.ma_kh
            LEFT JOIN nhan_vien  nv ON hd.ma_nv  = nv.ma_nv
        """
        params = []
        if tu_ngay and den_ngay:
            sql += f" WHERE DATE(hd.{dc}) BETWEEN %s AND %s"
            params = [tu_ngay, den_ngay]
        sql += f" ORDER BY hd.{dc} DESC"
        cursor.execute(sql, params)
        result = cursor.fetchall()
        conn.close()
        return result

    def get_invoice_detail(self, ma_hd: int) -> list:
        """Chi tiết từng dòng sản phẩm của hóa đơn."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sp.ten_sp, ct.don_gia, ct.so_luong,
                   ct.don_gia * ct.so_luong AS thanh_tien
            FROM chi_tiet_hoa_don ct
            JOIN san_pham sp ON ct.ma_sp = sp.ma_sp
            WHERE ct.ma_hd = %s
        """, (ma_hd,))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_customers(self) -> list:
        """Lấy danh sách khách hàng cho Combobox bán hàng."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ma_kh, ten_kh, so_dt FROM khach_hang ORDER BY ten_kh")
        result = cursor.fetchall()
        conn.close()
        return result


# ── Singleton + Backward-compatible wrappers ──────────────────
_service = SalesService()

def create_invoice(invoice: Invoice):          return _service.create_invoice(invoice)
def get_invoices(tu_ngay=None, den_ngay=None): return _service.get_invoices(tu_ngay, den_ngay)
def get_invoice_detail(ma_hd: int):            return _service.get_invoice_detail(ma_hd)
def get_customers() -> list:                   return _service.get_customers()