from backend.database.connection import get_connection
from backend.modules.auth_service import hash_password


def get_all() -> list:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT ma_nv, ten_nv, tai_khoan, vai_tro,
               COALESCE(so_dt,''), COALESCE(trang_thai,1)
        FROM nhan_vien ORDER BY ten_nv
    """)
    rows = cur.fetchall(); conn.close(); return rows


def add(ten, tk, mk, role, so_dt="") -> tuple:
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM nhan_vien WHERE tai_khoan=%s", (tk,))
        if cur.fetchone(): return False, "Tài khoản đã tồn tại!"
        cur.execute("""
            INSERT INTO nhan_vien (ten_nv, tai_khoan, mat_khau, vai_tro, so_dt)
            VALUES (%s,%s,%s,%s,%s)
        """, (ten, tk, hash_password(mk), role, so_dt))
        conn.commit(); return True, "Thêm nhân viên thành công!"
    except Exception as e:
        return False, str(e)
    finally: conn.close()


def update(ma_nv, ten, role, so_dt="", mk=None) -> tuple:
    conn = get_connection(); cur = conn.cursor()
    try:
        if mk:
            cur.execute("""
                UPDATE nhan_vien
                SET ten_nv=%s, vai_tro=%s, so_dt=%s, mat_khau=%s
                WHERE ma_nv=%s
            """, (ten, role, so_dt, hash_password(mk), ma_nv))
        else:
            cur.execute("""
                UPDATE nhan_vien SET ten_nv=%s, vai_tro=%s, so_dt=%s
                WHERE ma_nv=%s
            """, (ten, role, so_dt, ma_nv))
        conn.commit(); return True, "Cập nhật thành công!"
    except Exception as e:
        return False, str(e)
    finally: conn.close()


def toggle_status(ma_nv) -> tuple:
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute(
            "SELECT trang_thai FROM nhan_vien WHERE ma_nv=%s", (ma_nv,))
        row = cur.fetchone()
        if not row: return False, "Không tìm thấy nhân viên!"
        new_st = 0 if row[0] else 1
        cur.execute(
            "UPDATE nhan_vien SET trang_thai=%s WHERE ma_nv=%s",
            (new_st, ma_nv))
        conn.commit()
        return True, ("Đã khóa!" if new_st == 0 else "Đã mở khóa!")
    except Exception as e:
        return False, str(e)
    finally: conn.close()


def delete(ma_nv) -> tuple:
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE nhan_vien SET trang_thai=0 WHERE ma_nv=%s", (ma_nv,))
        conn.commit(); return True, "Đã ẩn nhân viên!"
    except Exception as e:
        return False, str(e)
    finally: conn.close()
