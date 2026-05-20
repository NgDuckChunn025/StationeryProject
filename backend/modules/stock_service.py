# backend/modules/stock_service.py
# ================================================================
# StockService — tạo phiếu nhập, cập nhật tồn kho
# Fix: xóa add_supplier() trùng → dùng supplier_service.add() thay thế
# ================================================================

from backend.database.connection import get_connection
from backend.models.stock_entry import StockEntry


class StockService:
    """Lớp service quản lý phiếu nhập kho."""

    def create_entry(self, entry: StockEntry) -> tuple[bool, int | str]:
        """
        Lưu phiếu nhập và cộng tồn kho trong một transaction.
        Trả về (True, ma_phieu) hoặc (False, thông báo lỗi).
        """
        if not entry.items:
            return False, "Phiếu nhập trống!"
        d = entry.to_dict()
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO phieu_nhap (ma_ncc, ma_nv, tong_tien, ghi_chu)
                VALUES (%s, %s, %s, %s)
            """, (d["ma_ncc"], d["ma_nv"], d["tong_tien"], d["ghi_chu"]))
            ma_phieu = cursor.lastrowid

            for item in d["items"]:
                cursor.execute("""
                    INSERT INTO chi_tiet_phieu_nhap (ma_phieu, ma_sp, so_luong, don_gia)
                    VALUES (%s, %s, %s, %s)
                """, (ma_phieu, item["ma_sp"], item["so_luong"], item["don_gia"]))
                cursor.execute("""
                    UPDATE san_pham SET ton_kho = ton_kho + %s WHERE ma_sp = %s
                """, (item["so_luong"], item["ma_sp"]))

            conn.commit()
            return True, ma_phieu
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def get_entries(self, tu_ngay=None, den_ngay=None) -> list:
        """Lấy danh sách phiếu nhập, có thể lọc theo khoảng ngày."""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT pn.ma_phieu,
                   COALESCE(ncc.ten_ncc, 'Chưa chọn'),
                   COALESCE(nv.ten_nv, '—'),
                   pn.ngay_nhap,
                   pn.tong_tien,
                   pn.ghi_chu
            FROM phieu_nhap pn
            LEFT JOIN nha_cung_cap ncc ON pn.ma_ncc = ncc.ma_ncc
            LEFT JOIN nhan_vien    nv  ON pn.ma_nv  = nv.ma_nv
        """
        params = []
        if tu_ngay and den_ngay:
            sql += " WHERE DATE(pn.ngay_nhap) BETWEEN %s AND %s"
            params = [tu_ngay, den_ngay]
        sql += " ORDER BY pn.ngay_nhap DESC"
        cursor.execute(sql, params)
        result = cursor.fetchall()
        conn.close()
        return result

    def get_entry_detail(self, ma_phieu: int) -> list:
        """Chi tiết từng dòng hàng của phiếu nhập."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sp.ten_sp, ct.don_gia, ct.so_luong,
                   ct.don_gia * ct.so_luong AS thanh_tien
            FROM chi_tiet_phieu_nhap ct
            JOIN san_pham sp ON ct.ma_sp = sp.ma_sp
            WHERE ct.ma_phieu = %s
        """, (ma_phieu,))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_suppliers(self) -> list:
        """
        Lấy danh sách nhà cung cấp đang hoạt động cho Combobox.
        Gọi qua supplier_service để tránh duplicate logic.
        """
        from backend.modules.supplier_service import get_dropdown
        rows = get_dropdown()          # [(ma_ncc, ten_ncc), ...]
        return [(r[0], r[1], "") for r in rows]   # thêm cột so_dt rỗng cho tương thích UI cũ

    # ── add_supplier() đã bị xóa ─────────────────────────────
    # Hàm này bị trùng với supplier_service.add().
    # Mọi chỗ gọi add_supplier() hãy dùng:
    #   from backend.modules import supplier_service as svc
    #   svc.add(Supplier(ten_ncc=..., so_dt=..., email=...))


# ── Singleton + Backward-compatible wrappers ──────────────────
_service = StockService()

def create_entry(entry: StockEntry):           return _service.create_entry(entry)
def get_entries(tu_ngay=None, den_ngay=None):  return _service.get_entries(tu_ngay, den_ngay)
def get_entry_detail(ma_phieu: int):           return _service.get_entry_detail(ma_phieu)
def get_suppliers() -> list:                   return _service.get_suppliers()