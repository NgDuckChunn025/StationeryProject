# backend/modules/product_service.py
# ================================================================
# ProductService — CRUD sản phẩm, tìm kiếm, cảnh báo tồn kho
# Tương thích cả DB cũ (không có cột mới) và DB mới
# ================================================================

from backend.database.connection import get_connection
from backend.models.product import Product


class ProductService:
    """Lớp service quản lý sản phẩm."""

    def _row_to_product(self, row) -> Product:
        return Product(
            ma_sp=row[0],
            ma_code=row[1],
            ten_sp=row[2],
            ten_loai=row[3] or "Chưa phân loại",
            don_vi=row[4] or "",
            gia_nhap=row[5] or 0,
            gia_ban=row[6] or 0,
            ton_kho=row[7] or 0,
            ma_loai=row[8] if len(row) > 8 else None,
            hinh_anh=row[9] if len(row) > 9 else ""
        )

    def get_all(self) -> list[Product]:
        """Lấy tất cả sản phẩm đang bán (trang_thai=1)."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT sp.ma_sp, sp.ma_code, sp.ten_sp,
       COALESCE(l.ten_loai, '') AS ten_loai,
       sp.don_vi,
       sp.gia_nhap,
       sp.gia_ban,
       sp.ton_kho,
       sp.ma_loai,
       sp.hinh_anh
                FROM san_pham sp
                LEFT JOIN loai_san_pham l ON sp.ma_loai = l.ma_loai
                WHERE COALESCE(sp.trang_thai, 1) = 1
                ORDER BY sp.ten_sp
            """)
        except Exception:
            cursor.execute("""
                SELECT ma_sp, ma_code, ten_sp,
                       COALESCE(ten_loai, '') AS ten_loai,
                       don_vi, gia_nhap, gia_ban, ton_kho
                FROM san_pham ORDER BY ten_sp
            """)
        result = [self._row_to_product(r) for r in cursor.fetchall()]
        conn.close()
        return result

    def get_by_id(self, ma_sp: int) -> Product | None:
        """Lấy một sản phẩm theo mã."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT sp.ma_sp, sp.ma_code, sp.ten_sp,
       COALESCE(l.ten_loai,'') AS ten_loai,
       sp.don_vi,
       sp.gia_nhap,
       sp.gia_ban,
       sp.ton_kho,
       sp.ma_loai,
       sp.hinh_anh
                FROM san_pham sp
                LEFT JOIN loai_san_pham l ON sp.ma_loai = l.ma_loai
                WHERE sp.ma_sp = %s
            """, (ma_sp,))
        except Exception:
            cursor.execute(
                "SELECT ma_sp, ma_code, ten_sp, '', don_vi, gia_nhap, gia_ban, ton_kho "
                "FROM san_pham WHERE ma_sp=%s", (ma_sp,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_product(row) if row else None

    def search(self, keyword: str) -> list[Product]:
        """Tìm sản phẩm theo tên hoặc mã code."""
        conn = get_connection()
        cursor = conn.cursor()
        kw = f"%{keyword}%"
        try:
            cursor.execute("""
                SELECT sp.ma_sp, sp.ma_code, sp.ten_sp,
       COALESCE(l.ten_loai, '') AS ten_loai,
       sp.don_vi,
       sp.gia_nhap,
       sp.gia_ban,
       sp.ton_kho,
       sp.ma_loai,
       sp.hinh_anh
                FROM san_pham sp
                LEFT JOIN loai_san_pham l ON sp.ma_loai = l.ma_loai
                WHERE COALESCE(sp.trang_thai, 1) = 1
                  AND (sp.ten_sp LIKE %s OR sp.ma_code LIKE %s)
                ORDER BY sp.ten_sp
            """, (kw, kw))
        except Exception:
            cursor.execute("""
                SELECT ma_sp, ma_code, ten_sp,
                       COALESCE(ten_loai, '') AS ten_loai,
                       don_vi, gia_nhap, gia_ban, ton_kho
                FROM san_pham
                WHERE ten_sp LIKE %s OR ma_code LIKE %s
                ORDER BY ten_sp
            """, (kw, kw))
        result = [self._row_to_product(r) for r in cursor.fetchall()]
        conn.close()
        return result

    def add(self, p: Product) -> tuple[bool, str]:
        """Thêm sản phẩm mới."""
        if not p.ma_code or not p.ten_sp:
            return False, "Mã sản phẩm và tên không được trống!"
        if p.gia_ban < p.gia_nhap:
            return False, "Giá bán không được thấp hơn giá nhập!"
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO san_pham
                    (ma_code, ten_sp, ma_loai, don_vi, gia_nhap, gia_ban, ton_kho, mo_ta)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (p.ma_code, p.ten_sp, p.ma_loai, p.don_vi,
                  p.gia_nhap, p.gia_ban, p.ton_kho, p.mo_ta or ""))
            conn.commit()
            return True, "Thêm sản phẩm thành công!"
        except Exception as e:
            if "mo_ta" in str(e):
                try:
                    cursor.execute("""
                        INSERT INTO san_pham
                            (ma_code, ten_sp, ma_loai, don_vi, gia_nhap, gia_ban, ton_kho)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (p.ma_code, p.ten_sp, p.ma_loai, p.don_vi,
                          p.gia_nhap, p.gia_ban, p.ton_kho))
                    conn.commit()
                    return True, "Thêm sản phẩm thành công!"
                except Exception as e2:
                    return False, f"Lỗi: {e2}"
            return False, "Mã sản phẩm đã tồn tại hoặc lỗi dữ liệu."
        finally:
            conn.close()

    def update(self, p: Product) -> tuple[bool, str]:
        """Cập nhật thông tin sản phẩm."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE san_pham
                SET ten_sp=%s, ma_loai=%s, don_vi=%s,
                    gia_nhap=%s, gia_ban=%s, ton_kho=%s, mo_ta=%s
                WHERE ma_sp=%s
            """, (p.ten_sp, p.ma_loai, p.don_vi, p.gia_nhap,
                  p.gia_ban, p.ton_kho, p.mo_ta or "", p.ma_sp))
            conn.commit()
            return True, "Cập nhật thành công!"
        except Exception as e:
            if "mo_ta" in str(e):
                try:
                    cursor.execute("""
                        UPDATE san_pham
                        SET ten_sp=%s, ma_loai=%s, don_vi=%s,
                            gia_nhap=%s, gia_ban=%s, ton_kho=%s
                        WHERE ma_sp=%s
                    """, (p.ten_sp, p.ma_loai, p.don_vi,
                          p.gia_nhap, p.gia_ban, p.ton_kho, p.ma_sp))
                    conn.commit()
                    return True, "Cập nhật thành công!"
                except Exception as e2:
                    return False, str(e2)
            return False, str(e)
        finally:
            conn.close()

    def delete(self, ma_sp: int) -> tuple[bool, str]:
        """Ẩn sản phẩm (soft delete — không xóa khỏi DB)."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE san_pham SET trang_thai=0 WHERE ma_sp=%s", (ma_sp,))
            conn.commit()
            return True, "Đã ẩn sản phẩm!"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def get_low_stock(self, threshold: int = 10) -> list[Product]:
        """Lấy danh sách sản phẩm tồn kho thấp."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT sp.ma_sp, sp.ma_code, sp.ten_sp,
       COALESCE(l.ten_loai,'') AS ten_loai,
       sp.don_vi,
       sp.gia_nhap,
       sp.gia_ban,
       sp.ton_kho,
       sp.ma_loai,
       sp.hinh_anh
                FROM san_pham sp
                LEFT JOIN loai_san_pham l ON sp.ma_loai = l.ma_loai
                WHERE sp.ton_kho <= %s AND COALESCE(sp.trang_thai, 1) = 1
                ORDER BY sp.ton_kho ASC
            """, (threshold,))
        except Exception:
            cursor.execute("""
                SELECT ma_sp, ma_code, ten_sp, '', don_vi, gia_nhap, gia_ban, ton_kho
                FROM san_pham WHERE ton_kho <= %s ORDER BY ton_kho ASC
            """, (threshold,))
        result = [self._row_to_product(r) for r in cursor.fetchall()]
        conn.close()
        return result

    def get_categories(self) -> list[dict]:
        """Lấy danh sách loại sản phẩm để dùng trong Combobox."""
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


# ── Singleton + Backward-compatible wrappers ──────────────────
_service = ProductService()

def get_all() -> list[Product]:            return _service.get_all()
def get_by_id(ma_sp: int):                 return _service.get_by_id(ma_sp)
def search(keyword: str) -> list[Product]: return _service.search(keyword)
def add(p: Product) -> tuple[bool, str]:   return _service.add(p)
def update(p: Product) -> tuple[bool, str]:return _service.update(p)
def delete(ma_sp: int) -> tuple[bool, str]:return _service.delete(ma_sp)
def get_low_stock(threshold=10):           return _service.get_low_stock(threshold)
def get_categories() -> list[dict]:        return _service.get_categories()