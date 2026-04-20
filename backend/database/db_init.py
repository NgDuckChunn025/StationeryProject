# backend/database/db_init.py
# ================================================================
# Tạo database và toàn bộ bảng trong MySQL
# ================================================================

import mysql.connector
from mysql.connector import Error
from backend.database.connection import DB_CONFIG
import bcrypt


def tao_database():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            charset="utf8mb4",
        )
        cursor = conn.cursor()

        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute(f"USE {DB_CONFIG['database']}")

        print(f" Database '{DB_CONFIG['database']}' sẵn sàng")

        _tao_cac_bang(cursor)
        conn.commit()

        _tao_admin_mac_dinh(cursor, conn)
        _them_du_lieu_mau(cursor, conn)

        cursor.close()
        conn.close()

        print(" Khởi tạo database hoàn tất!\n")
        return True

    except Error as e:
        print(f" Lỗi khởi tạo database: {e}")
        return False


# ================================================================
# TẠO BẢNG
# ================================================================
def _tao_cac_bang(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loai_san_pham (
            ma_loai  INT AUTO_INCREMENT PRIMARY KEY,
            ten_loai VARCHAR(100) NOT NULL,
            mo_ta    VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS san_pham (
            ma_sp     INT AUTO_INCREMENT PRIMARY KEY,
            ma_code   VARCHAR(20) UNIQUE NOT NULL,
            ten_sp    VARCHAR(200) NOT NULL,
            ma_loai   INT,
            don_vi    VARCHAR(50),
            gia_nhap  DECIMAL(15,0) DEFAULT 0,
            gia_ban   DECIMAL(15,0) DEFAULT 0,
            ton_kho   INT DEFAULT 0,
            trang_thai TINYINT(1) DEFAULT 1,
            FOREIGN KEY (ma_loai) REFERENCES loai_san_pham(ma_loai)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS khach_hang (
            ma_kh INT AUTO_INCREMENT PRIMARY KEY,
            ten_kh VARCHAR(200),
            so_dt VARCHAR(20),
            dia_chi VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nhan_vien (
            ma_nv INT AUTO_INCREMENT PRIMARY KEY,
            ten_nv VARCHAR(200),
            tai_khoan VARCHAR(50) UNIQUE,
            mat_khau VARCHAR(255),
            vai_tro VARCHAR(20)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hoa_don (
            ma_hd INT AUTO_INCREMENT PRIMARY KEY,
            ma_nv INT,
            tong_tien FLOAT,
            giam_gia FLOAT,
            ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ma_nv) REFERENCES nhan_vien(ma_nv)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chi_tiet_hoa_don (
            ma_ct INT AUTO_INCREMENT PRIMARY KEY,
            ma_hd INT,
            ma_sp INT,
            so_luong INT,
            don_gia FLOAT,
            FOREIGN KEY (ma_hd) REFERENCES hoa_don(ma_hd),
            FOREIGN KEY (ma_sp) REFERENCES san_pham(ma_sp)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nhap_kho (
            ma_nhap INT AUTO_INCREMENT PRIMARY KEY,
            ma_sp INT,
            so_luong INT,
            gia_nhap FLOAT,
            ngay_nhap DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ma_sp) REFERENCES san_pham(ma_sp)
        )
    """)

    print(" Tạo bảng thành công")


# ================================================================
# ADMIN
# ================================================================
def _tao_admin_mac_dinh(cursor, conn):
    cursor.execute("SELECT COUNT(*) FROM nhan_vien WHERE tai_khoan='admin'")
    if cursor.fetchone()[0] == 0:
        mk = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO nhan_vien (ten_nv, tai_khoan, mat_khau, vai_tro) VALUES (%s,%s,%s,%s)",
            ("Admin", "admin", mk, "admin")
        )
        conn.commit()
        print(" Tạo admin: admin / 123456")


# ================================================================
# DỮ LIỆU MẪU
# ================================================================
def _them_du_lieu_mau(cursor, conn):

    # loại
    cursor.execute("SELECT COUNT(*) FROM loai_san_pham")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO loai_san_pham (ten_loai) VALUES (%s)
        """, [
            ("Bút",),
            ("Vở",),
            ("Giấy",),
            ("Dụng cụ",)
        ])
        conn.commit()

    # sản phẩm
    cursor.execute("SELECT COUNT(*) FROM san_pham")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO san_pham (ma_code, ten_sp, ma_loai, don_vi, gia_nhap, gia_ban, ton_kho)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, [
            ("SP01", "Bút bi", 1, "cây", 2000, 5000, 100),
            ("SP02", "Bút chì", 1, "cây", 1000, 3000, 80),
            ("SP03", "Vở 200 trang", 2, "quyển", 10000, 15000, 50),
            ("SP04", "Giấy A4", 3, "ram", 60000, 75000, 30),
            ("SP05", "Thước kẻ", 4, "cái", 3000, 7000, 40)
        ])
        conn.commit()

    # khách hàng
    cursor.execute("SELECT COUNT(*) FROM khach_hang")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO khach_hang (ten_kh, so_dt, dia_chi)
            VALUES (%s,%s,%s)
        """, [
            ("Nguyễn Văn A", "0988888888", "Hà Nội"),
            ("Trần Thị B", "0977777777", "Hưng Yên")
        ])
        conn.commit()

    print(" Thêm dữ liệu mẫu xong")