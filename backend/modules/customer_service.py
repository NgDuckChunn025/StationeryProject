# backend/modules/customer_service.py
from backend.database.connection import get_connection
from backend.models.customer import Customer


def get_all(keyword: str = "") -> list:
    conn = get_connection(); cur = conn.cursor()
    if keyword:
        kw = f"%{keyword}%"
        cur.execute("""
            SELECT ma_kh,
       ten_kh,
       so_dt,
       dia_chi,
       email,
       COALESCE(diem_tich_luy, 0),
       COALESCE(hang_khach_hang, 'Thường'),
       COALESCE(tong_chi_tieu, 0)
            FROM khach_hang
            WHERE ten_kh LIKE %s OR so_dt LIKE %s OR email LIKE %s
            ORDER BY ten_kh
        """, (kw, kw, kw))
    else:
        cur.execute("""
            SELECT ma_kh,
       ten_kh,
       so_dt,
       dia_chi,
       email,
       COALESCE(diem_tich_luy, 0),
       COALESCE(hang_khach_hang, 'Thường'),
       COALESCE(tong_chi_tieu, 0)
            FROM khach_hang ORDER BY ten_kh
        """)
    result = [Customer.from_row(r) for r in cur.fetchall()]
    conn.close()
    return result


def get_by_id(ma_kh: int):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SSELECT ma_kh,
       ten_kh,
       so_dt,
       dia_chi,
       email,
       COALESCE(diem_tich_luy, 0),
       COALESCE(hang_khach_hang, 'Thường'),
       COALESCE(tong_chi_tieu, 0)
        FROM khach_hang WHERE ma_kh = %s
    """, (ma_kh,))
    row = cur.fetchone()
    conn.close()
    return Customer.from_row(row) if row else None


def add(c: Customer) -> tuple:
    ok, msg = c.validate()
    if not ok:
        return False, msg
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO khach_hang (ten_kh, so_dt, dia_chi, email)
            VALUES (%s, %s, %s, %s)
        """, (c.ten_kh, c.so_dt, c.dia_chi, c.email))
        conn.commit()
        return True, "Thêm khách hàng thành công!"
    except Exception as e:
        return False, f"Lỗi: {e}"
    finally:
        conn.close()


def update(c: Customer) -> tuple:
    ok, msg = c.validate()
    if not ok:
        return False, msg
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE khach_hang
            SET ten_kh=%s, so_dt=%s, dia_chi=%s, email=%s
            WHERE ma_kh=%s
        """, (c.ten_kh, c.so_dt, c.dia_chi, c.email, c.ma_kh))
        conn.commit()
        return True, "Cập nhật thành công!"
    except Exception as e:
        return False, f"Lỗi: {e}"
    finally:
        conn.close()


def delete(ma_kh: int) -> tuple:
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM khach_hang WHERE ma_kh=%s", (ma_kh,))
        conn.commit()
        return True, "Đã xóa khách hàng!"
    except Exception as e:
        return False, f"Lỗi: {e}"
    finally:
        conn.close()


def _get_nguong() -> tuple:
    """Lấy ngưỡng hạng từ config, fallback về mặc định."""
    try:
        from backend.modules.config_service import get_int
        return (get_int("nguong_hang_bac",     500_000),
                get_int("nguong_hang_vang",   2_000_000),
                get_int("nguong_hang_bachkim",5_000_000))
    except Exception:
        return 500_000, 2_000_000, 5_000_000


def _hang_from_chi_tieu(chi_tieu: float) -> str:
    ng_bac, ng_vang, ng_bk = _get_nguong()
    if chi_tieu >= ng_bk:  return "Bạch Kim"
    if chi_tieu >= ng_vang: return "Vàng"
    if chi_tieu >= ng_bac:  return "Bạc"
    return "Thường"


def cap_nhat_sau_mua(ma_kh: int,
                     so_tien: float,
                     so_diem_tru: int = 0) -> bool:
    """
    Gọi sau khi tạo hóa đơn thành công:
      - Cộng so_tien vào tong_chi_tieu
      - Tính diem_them = so_tien // ty_le_tich_diem
      - diem_cuoi = diem_hien_tai + diem_them - so_diem_tru (min 0)
      - Cập nhật hang_khach_hang dựa trên tong_chi_tieu mới
    """
    if not ma_kh:
        return False
    try:
        from backend.modules.config_service import get_int
        ty_le = get_int("ty_le_tich_diem", 10_000)
    except Exception:
        ty_le = 10_000

    diem_them = int(so_tien // ty_le)

    conn = get_connection(); cur = conn.cursor()
    try:
        # Cộng chi tiêu thực tế (sau giảm giá điểm, trước giảm tiền mặt)
        cur.execute("""
            UPDATE khach_hang
            SET tong_chi_tieu = COALESCE(tong_chi_tieu, 0) + %s
            WHERE ma_kh = %s
        """, (so_tien, ma_kh))

        # Cập nhật điểm (thêm - trừ, tối thiểu 0)
        cur.execute("""
            UPDATE khach_hang
            SET diem_tich_luy = GREATEST(0,
                COALESCE(diem_tich_luy, 0) + %s - %s)
            WHERE ma_kh = %s
        """, (diem_them, so_diem_tru, ma_kh))

        # Lấy tong_chi_tieu mới để xếp hạng
        cur.execute(
            "SELECT COALESCE(tong_chi_tieu, 0) FROM khach_hang WHERE ma_kh=%s",
            (ma_kh,))
        row = cur.fetchone()
        chi_tieu_moi = float(row[0]) if row else 0.0
        hang_moi = _hang_from_chi_tieu(chi_tieu_moi)

        cur.execute("""
            UPDATE khach_hang
            SET hang_khach_hang = %s
            WHERE ma_kh = %s
        """, (hang_moi, ma_kh))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[cap_nhat_sau_mua] {e}")
        return False
    finally:
        conn.close()


def add_points(ma_kh: int, diem: int) -> bool:
    """Cộng/trừ điểm đơn thuần (không đổi chi tiêu, không đổi hạng)."""
    if not ma_kh:
        return False
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE khach_hang
            SET diem_tich_luy = GREATEST(0,
                COALESCE(diem_tich_luy, 0) + %s)
            WHERE ma_kh = %s
        """, (diem, ma_kh))
        conn.commit()
        return True
    except Exception as e:
        print(f"[add_points] {e}")
        return False
    finally:
        conn.close()


class CustomerService:
    pass