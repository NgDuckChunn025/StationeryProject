from backend.database.connection import get_connection
from backend.modules.auth_service import hash_password



def get_all():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ma_nv, ten_nv, tai_khoan, vai_tro
        FROM nhan_vien
        ORDER BY ten_nv
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def add(ten, tk, mk, role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # check trùng tài khoản
        cursor.execute("SELECT * FROM nhan_vien WHERE tai_khoan=%s", (tk,))
        if cursor.fetchone():
            return False, "Tài khoản đã tồn tại"

        cursor.execute("""
            INSERT INTO nhan_vien (ten_nv, tai_khoan, mat_khau, vai_tro)
            VALUES (%s,%s,%s,%s)
        """, (ten, tk, hash_password(mk), role))

        conn.commit()
        return True, "Thêm nhân viên thành công!"

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def delete(ma_nv):
    conn = get_connection()
    cursor = conn.cursor()

    # demo thì xóa thẳng luôn cho đơn giản
    cursor.execute("DELETE FROM nhan_vien WHERE ma_nv=%s", (ma_nv,))
    conn.commit()
    conn.close()

    return True, "Đã xóa"