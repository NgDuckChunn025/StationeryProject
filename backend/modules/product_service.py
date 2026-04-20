# backend/modules/product_service.py
# ================================================================
# Nghiệp vụ sản phẩm: CRUD, tìm kiếm, tồn kho
# ================================================================

from backend.database.connection import get_connection
from backend.models.product import Product


# ================================================================
# LẤY DANH SÁCH
# ================================================================
def get_all() -> list[Product]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sp.ma_sp, sp.ma_code, sp.ten_sp, l.ten_loai,
               sp.don_vi, sp.gia_nhap, sp.gia_ban, sp.ton_kho, sp.ma_loai
        FROM san_pham sp
        LEFT JOIN loai_san_pham l ON sp.ma_loai = l.ma_loai
        WHERE sp.trang_thai = 1
        ORDER BY sp.ten_sp
    """)
    result = [Product.from_row(r) for r in cursor.fetchall()]
    conn.close()
    return result


# ================================================================
# TÌM KIẾM
# ================================================================
def search(keyword: str) -> list[Product]:
    conn = get_connection()
    cursor = conn.cursor()
    kw = f"%{keyword}%"
    cursor.execute("""
        SELECT sp.ma_sp, sp.ma_code, sp.ten_sp, l.ten_loai,
               sp.don_vi, sp.gia_nhap, sp.gia_ban, sp.ton_kho, sp.ma_loai
        FROM san_pham sp
        LEFT JOIN loai_san_pham l ON sp.ma_loai = l.ma_loai
        WHERE sp.trang_thai = 1
          AND (sp.ten_sp LIKE %s OR sp.ma_code LIKE %s)
        ORDER BY sp.ten_sp
    """, (kw, kw))
    result = [Product.from_row(r) for r in cursor.fetchall()]
    conn.close()
    return result


# ================================================================
# LẤY THEO ID (RẤT QUAN TRỌNG)
# ================================================================
def get_by_id(ma_sp: int) -> Product | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sp.ma_sp, sp.ma_code, sp.ten_sp, l.ten_loai,
               sp.don_vi, sp.gia_nhap, sp.gia_ban, sp.ton_kho, sp.ma_loai
        FROM san_pham sp
        LEFT JOIN loai_san_pham l ON sp.ma_loai = l.ma_loai
        WHERE sp.ma_sp = %s
    """, (ma_sp,))
    row = cursor.fetchone()
    conn.close()
    return Product.from_row(row) if row else None


# ================================================================
# THÊM SẢN PHẨM
# ================================================================
def add(p: Product) -> tuple[bool, str]:
    # Validate
    if not p.ma_code or not p.ten_sp:
        return False, "Mã sản phẩm và tên không được trống!"

    if p.gia_nhap < 0 or p.gia_ban < 0:
        return False, "Giá không hợp lệ!"

    if p.gia_ban < p.gia_nhap:
        return False, "Giá bán không được thấp hơn giá nhập!"

    if p.ton_kho < 0:
        return False, "Tồn kho không hợp lệ!"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO san_pham (
                ma_code, ten_sp, ma_loai, don_vi,
                gia_nhap, gia_ban, ton_kho, mo_ta
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            p.ma_code,
            p.ten_sp,
            p.ma_loai,
            p.don_vi,
            p.gia_nhap,
            p.gia_ban,
            p.ton_kho,
            getattr(p, "mo_ta", None)  # FIX lỗi
        ))

        conn.commit()
        return True, "Thêm sản phẩm thành công!"

    except Exception as e:
        return False, f"Lỗi: {str(e)}"

    finally:
        conn.close()


# ================================================================
# CẬP NHẬT
# ================================================================
def update(p: Product) -> tuple[bool, str]:
    if p.gia_nhap < 0 or p.gia_ban < 0:
        return False, "Giá không hợp lệ!"

    if p.ton_kho < 0:
        return False, "Tồn kho không hợp lệ!"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE san_pham
            SET ten_sp=%s,
                ma_loai=%s,
                don_vi=%s,
                gia_nhap=%s,
                gia_ban=%s,
                ton_kho=%s,
                mo_ta=%s
            WHERE ma_sp=%s
        """, (
            p.ten_sp,
            p.ma_loai,
            p.don_vi,
            p.gia_nhap,
            p.gia_ban,
            p.ton_kho,
            getattr(p, "mo_ta", None),
            p.ma_sp
        ))

        conn.commit()
        return True, "Cập nhật thành công!"

    except Exception as e:
        return False, f"Lỗi: {str(e)}"

    finally:
        conn.close()


# ================================================================
# XOÁ (SOFT DELETE)
# ================================================================
def delete(ma_sp: int) -> tuple[bool, str]:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE san_pham SET trang_thai=0 WHERE ma_sp=%s",
            (ma_sp,)
        )
        conn.commit()
        return True, "Đã xóa sản phẩm!"

    except Exception as e:
        return False, f"Lỗi: {str(e)}"

    finally:
        conn.close()


# ================================================================
# SẮP HẾT HÀNG
# ================================================================
def get_low_stock(threshold=10) -> list[Product]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ma_sp, ma_code, ten_sp, NULL, don_vi,
               gia_nhap, gia_ban, ton_kho, ma_loai
        FROM san_pham
        WHERE ton_kho <= %s AND trang_thai = 1
        ORDER BY ton_kho ASC
    """, (threshold,))

    result = [Product.from_row(r) for r in cursor.fetchall()]
    conn.close()
    return result


# ================================================================
# DANH MỤC
# ================================================================
def get_categories() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ma_loai, ten_loai
        FROM loai_san_pham
        ORDER BY ten_loai
    """)

    result = [{"ma": r[0], "ten": r[1]} for r in cursor.fetchall()]
    conn.close()
    return result


# ================================================================
# CẬP NHẬT TỒN KHO (RẤT QUAN TRỌNG)
# ================================================================
def update_stock(ma_sp: int, so_luong: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE san_pham
        SET ton_kho = ton_kho + %s
        WHERE ma_sp = %s
    """, (so_luong, ma_sp))

    conn.commit()
    conn.close()