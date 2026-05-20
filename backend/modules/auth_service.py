# backend/modules/auth_service.py
# ================================================================
# AuthService — xác thực người dùng, phân quyền, hash mật khẩu
# ================================================================

import bcrypt
from backend.database.connection import get_connection


class AuthService:
    """Lớp service xác thực và phân quyền nhân viên."""

    def login(self, tai_khoan: str, mat_khau: str) -> dict | None:
        """Kiểm tra đăng nhập. Trả dict user info hoặc None nếu sai."""
        conn = get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ma_nv, ten_nv, tai_khoan, mat_khau, vai_tro
                FROM nhan_vien
                WHERE tai_khoan = %s AND trang_thai = 1
            """, (tai_khoan,))
            row = cursor.fetchone()
            if row and bcrypt.checkpw(mat_khau.encode(), row[3].encode()):
                return {
                    "ma_nv":    row[0],
                    "ten_nv":   row[1],
                    "tai_khoan": row[2],
                    "vai_tro":  row[4],
                }
        except Exception as e:
            print("Lỗi login:", e)
        finally:
            conn.close()
        return None

    def is_admin(self, nv: dict) -> bool:
        """Kiểm tra vai trò quản trị."""
        return nv.get("vai_tro") == "admin"

    def hash_password(self, mat_khau: str) -> str:
        """Hash mật khẩu bằng bcrypt."""
        return bcrypt.hashpw(mat_khau.encode(), bcrypt.gensalt()).decode()

    def change_password(self, ma_nv: int, cu: str, moi: str) -> tuple[bool, str]:
        """Đổi mật khẩu sau khi xác minh mật khẩu cũ."""
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
            cursor.execute(
                "UPDATE nhan_vien SET mat_khau=%s WHERE ma_nv=%s",
                (self.hash_password(moi), ma_nv)
            )
            conn.commit()
            return True, "Đổi mật khẩu thành công!"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()


# ── Singleton + Backward-compatible wrappers ──────────────────
# Giữ nguyên để toàn bộ View/UI không cần sửa import
_service = AuthService()

def login(tai_khoan: str, mat_khau: str) -> dict | None:
    return _service.login(tai_khoan, mat_khau)

def is_admin(nv: dict) -> bool:
    return _service.is_admin(nv)

def hash_password(mat_khau: str) -> str:
    return _service.hash_password(mat_khau)

def change_password(ma_nv: int, cu: str, moi: str) -> tuple[bool, str]:
    return _service.change_password(ma_nv, cu, moi)