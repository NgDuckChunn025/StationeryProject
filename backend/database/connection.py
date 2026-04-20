# backend/database/connection.py
# ================================================================
# Kết nối MySQL bằng mysql-connector-python
# ================================================================

import mysql.connector
from mysql.connector import Error

# ---- Chỉnh sửa thông tin kết nối tại đây ----
DB_CONFIG = {
    "host"    : "localhost",   # Địa chỉ server MySQL
    "port"    : 3306,          # Cổng mặc định MySQL
    "user"    : "root",        # Tài khoản MySQL
    "password": "Chung021205#",      # Mật khẩu MySQL
    "database": "stationery_db",
    "charset" : "utf8mb4",
    "use_unicode": True,
}


def get_connection():
    """Tạo và trả về kết nối MySQL mới."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[LỖI KẾT NỐI] {e}")
        return None


def test_connection():
    """Kiểm tra kết nối. Trả về True nếu thành công."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        if conn.is_connected():
            conn.close()
            return True
    except Error:
        pass
    return False