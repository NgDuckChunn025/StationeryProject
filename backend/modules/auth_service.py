# backend/modules/auth_service.py
# ================================================================
# Xác thực người dùng — bcrypt
# ================================================================

import bcrypt
from backend.database.connection import get_connection


def login(tai_khoan: str, mat_khau: str) -> dict | None:
    """
    Kiểm tra đăng nhập
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ma_nv, ten_nv, tai_khoan, mat_khau, vai_tro
            FROM nhan_vien
            WHERE tai_khoan = %s
        """, (tai_khoan,))

        row = cursor.fetchone()

        if row:
            db_password = row[3]

            # kiểm tra mật khẩu
            if bcrypt.checkpw(mat_khau.encode(), db_password.encode()):
                return {
                    "ma_nv": row[0],
                    "ten_nv": row[1],
                    "tai_khoan": row[2],
                    "vai_tro": row[4]
                }

    except Exception as e:
        print("Lỗi login:", e)

    finally:
        conn.close()

    return None


# ================================================================
# PHÂN QUYỀN
# ================================================================
def is_admin(nv: dict) -> bool:
    return nv.get("vai_tro") == "admin"


# ================================================================
# HASH PASSWORD
# ================================================================
def hash_password(mat_khau: str) -> str:
    return bcrypt.hashpw(mat_khau.encode(), bcrypt.gensalt()).decode()


# ================================================================
# ĐỔI MẬT KHẨU
# ================================================================
def change_password(ma_nv: int, cu: str, moi: str) -> tuple[bool, str]:
    conn = get_connection()
    if not conn:
        return False, "Không kết nối DB"

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT mat_khau FROM nhan_vien WHERE ma_nv=%s", (ma_nv,))
        row = cursor.fetchone()

        if not row:
            return False, "Không tìm thấy tài khoản!"

        if not bcrypt.checkpw(cu.encode(), row[0].encode()):
            return False, "Mật khẩu cũ không đúng!"

        cursor.execute("""
            UPDATE nhan_vien
            SET mat_khau=%s
            WHERE ma_nv=%s
        """, (hash_password(moi), ma_nv))

        conn.commit()
        return True, "Đổi mật khẩu thành công!"

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()