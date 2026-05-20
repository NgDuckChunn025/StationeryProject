# backend/modules/category_service.py
# ================================================================
# CategoryService — CRUD loại sản phẩm
# Fix: ProductCategory đã có model nhưng thiếu service
# ================================================================

from backend.database.connection import get_connection
from backend.models.product_category import ProductCategory


class CategoryService:
    """Lớp service quản lý loại/danh mục sản phẩm."""

    def get_all(self, keyword: str = "") -> list[ProductCategory]:
        """Lấy tất cả loại sản phẩm."""
        conn = get_connection()
        cursor = conn.cursor()
        if keyword:
            kw = f"%{keyword}%"
            cursor.execute("""
                SELECT ma_loai, ten_loai, mo_ta
                FROM loai_san_pham
                WHERE ten_loai LIKE %s
                ORDER BY ten_loai
            """, (kw,))
        else:
            cursor.execute("""
                SELECT ma_loai, ten_loai, mo_ta
                FROM loai_san_pham ORDER BY ten_loai
            """)
        result = [ProductCategory.from_row(r) for r in cursor.fetchall()]
        conn.close()
        return result

    def get_by_id(self, ma_loai: int) -> ProductCategory | None:
        """Lấy một loại sản phẩm theo mã."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ma_loai, ten_loai, mo_ta
            FROM loai_san_pham WHERE ma_loai = %s
        """, (ma_loai,))
        row = cursor.fetchone()
        conn.close()
        return ProductCategory.from_row(row) if row else None

    def add(self, cat: ProductCategory) -> tuple[bool, str]:
        """Thêm loại sản phẩm mới."""
        ok, msg = cat.validate()
        if not ok:
            return False, msg
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT ma_loai FROM loai_san_pham WHERE ten_loai=%s",
                (cat.ten_loai,))
            if cursor.fetchone():
                return False, f"Loại '{cat.ten_loai}' đã tồn tại!"
            cursor.execute("""
                INSERT INTO loai_san_pham (ten_loai, mo_ta)
                VALUES (%s, %s)
            """, (cat.ten_loai, cat.mo_ta or ""))
            conn.commit()
            return True, "Thêm loại sản phẩm thành công!"
        except Exception as e:
            return False, f"Lỗi: {e}"
        finally:
            conn.close()

    def update(self, cat: ProductCategory) -> tuple[bool, str]:
        """Cập nhật tên và mô tả loại sản phẩm."""
        ok, msg = cat.validate()
        if not ok:
            return False, msg
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE loai_san_pham SET ten_loai=%s, mo_ta=%s
                WHERE ma_loai=%s
            """, (cat.ten_loai, cat.mo_ta or "", cat.ma_loai))
            conn.commit()
            return True, "Cập nhật loại sản phẩm thành công!"
        except Exception as e:
            return False, f"Lỗi: {e}"
        finally:
            conn.close()

    def delete(self, ma_loai: int) -> tuple[bool, str]:
        """Xóa loại sản phẩm nếu không còn sản phẩm thuộc loại này."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM san_pham WHERE ma_loai=%s", (ma_loai,))
            if cursor.fetchone()[0] > 0:
                return False, "Không thể xóa! Vẫn còn sản phẩm thuộc loại này."
            cursor.execute(
                "DELETE FROM loai_san_pham WHERE ma_loai=%s", (ma_loai,))
            conn.commit()
            return True, "Đã xóa loại sản phẩm!"
        except Exception as e:
            return False, f"Lỗi: {e}"
        finally:
            conn.close()

    def get_dropdown(self) -> list[dict]:
        """Trả list [{'ma': ..., 'ten': ...}] để dùng trong Combobox."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT ma_loai, ten_loai FROM loai_san_pham ORDER BY ten_loai")
            result = [{"ma": r[0], "ten": r[1]} for r in cursor.fetchall()]
        except Exception:
            result = []
        conn.close()
        return result

    def count_products(self, ma_loai: int) -> int:
        """Đếm số sản phẩm thuộc loại này."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM san_pham WHERE ma_loai=%s AND COALESCE(trang_thai,1)=1",
            (ma_loai,))
        count = cursor.fetchone()[0]
        conn.close()
        return count


# ── Singleton + Backward-compatible wrappers ──────────────────
_service = CategoryService()

def get_all(keyword: str = ""):             return _service.get_all(keyword)
def get_by_id(ma_loai: int):               return _service.get_by_id(ma_loai)
def add(cat: ProductCategory):             return _service.add(cat)
def update(cat: ProductCategory):          return _service.update(cat)
def delete(ma_loai: int):                  return _service.delete(ma_loai)
def get_dropdown() -> list[dict]:          return _service.get_dropdown()
def count_products(ma_loai: int) -> int:   return _service.count_products(ma_loai)