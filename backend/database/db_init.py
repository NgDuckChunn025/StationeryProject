# backend/database/db_init.py
# ================================================================
# Tạo database và toàn bộ bảng trong MySQL
# ================================================================

import mysql.connector
from mysql.connector import Error
from backend.database.connection import DB_CONFIG
import bcrypt


def tao_database():
    """Tạo database nếu chưa có, rồi tạo các bảng."""
    try:
        # Kết nối không chỉ định database để tạo mới
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


def _tao_cac_bang(cursor):
    """Tạo tất cả bảng cần thiết."""

    # 1. Loại sản phẩm
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loai_san_pham (
            ma_loai  INT AUTO_INCREMENT PRIMARY KEY,
            ten_loai VARCHAR(100) NOT NULL,
            mo_ta    VARCHAR(255)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 2. Sản phẩm
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS san_pham (
            ma_sp     INT AUTO_INCREMENT PRIMARY KEY,
            ma_code   VARCHAR(20)  UNIQUE NOT NULL,
            ten_sp    VARCHAR(200) NOT NULL,
            ma_loai   INT,
            don_vi    VARCHAR(50),
            gia_nhap  DECIMAL(15,0) DEFAULT 0,
            gia_ban   DECIMAL(15,0) DEFAULT 0,
            ton_kho   INT           DEFAULT 0,
            mo_ta     TEXT,
            trang_thai TINYINT(1)   DEFAULT 1,
            FOREIGN KEY (ma_loai) REFERENCES loai_san_pham(ma_loai)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 3. Nhà cung cấp
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nha_cung_cap (
            ma_ncc  INT AUTO_INCREMENT PRIMARY KEY,
            ten_ncc VARCHAR(200) NOT NULL,
            dia_chi VARCHAR(300),
            so_dt   VARCHAR(20),
            email   VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 4. Khách hàng
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS khach_hang (
            ma_kh        INT AUTO_INCREMENT PRIMARY KEY,
            ten_kh       VARCHAR(200) NOT NULL,
            so_dt        VARCHAR(20),
            dia_chi      VARCHAR(300),
            email        VARCHAR(100),
            diem_tich_luy INT DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 5. Nhân viên
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nhan_vien (
            ma_nv     INT AUTO_INCREMENT PRIMARY KEY,
            ten_nv    VARCHAR(200) NOT NULL,
            tai_khoan VARCHAR(50)  UNIQUE NOT NULL,
            mat_khau  VARCHAR(255) NOT NULL,
            vai_tro   VARCHAR(20)  DEFAULT 'nhanvien',
            so_dt     VARCHAR(20),
            trang_thai TINYINT(1)  DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 6. Hóa đơn
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hoa_don (
            ma_hd       INT AUTO_INCREMENT PRIMARY KEY,
            ma_kh       INT,
            ma_nv       INT,
            ngay_ban    DATETIME     DEFAULT CURRENT_TIMESTAMP,
            tong_tien   DECIMAL(15,0) DEFAULT 0,
            giam_gia    DECIMAL(15,0) DEFAULT 0,
            thanh_toan  DECIMAL(15,0) DEFAULT 0,
            hinh_thuc   VARCHAR(50)  DEFAULT 'Tiền mặt',
            FOREIGN KEY (ma_kh) REFERENCES khach_hang(ma_kh),
            FOREIGN KEY (ma_nv) REFERENCES nhan_vien(ma_nv)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 7. Chi tiết hóa đơn
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chi_tiet_hoa_don (
            ma_ct   INT AUTO_INCREMENT PRIMARY KEY,
            ma_hd   INT NOT NULL,
            ma_sp   INT NOT NULL,
            so_luong INT          DEFAULT 1,
            don_gia  DECIMAL(15,0) DEFAULT 0,
            FOREIGN KEY (ma_hd) REFERENCES hoa_don(ma_hd),
            FOREIGN KEY (ma_sp) REFERENCES san_pham(ma_sp)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 8. Phiếu nhập kho
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phieu_nhap (
            ma_phieu INT AUTO_INCREMENT PRIMARY KEY,
            ma_ncc   INT,
            ma_nv    INT,
            ngay_nhap DATETIME    DEFAULT CURRENT_TIMESTAMP,
            tong_tien DECIMAL(15,0) DEFAULT 0,
            ghi_chu  TEXT,
            FOREIGN KEY (ma_ncc) REFERENCES nha_cung_cap(ma_ncc),
            FOREIGN KEY (ma_nv)  REFERENCES nhan_vien(ma_nv)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 9. Chi tiết phiếu nhập
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chi_tiet_phieu_nhap (
            ma_ct    INT AUTO_INCREMENT PRIMARY KEY,
            ma_phieu INT NOT NULL,
            ma_sp    INT NOT NULL,
            so_luong INT           DEFAULT 1,
            don_gia  DECIMAL(15,0) DEFAULT 0,
            FOREIGN KEY (ma_phieu) REFERENCES phieu_nhap(ma_phieu),
            FOREIGN KEY (ma_sp)    REFERENCES san_pham(ma_sp)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    print(" Tạo 9 bảng thành công")


def _tao_admin_mac_dinh(cursor, conn):
    cursor.execute("SELECT COUNT(*) FROM nhan_vien WHERE tai_khoan='admin'")
    if cursor.fetchone()[0] == 0:
        mk = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO nhan_vien (ten_nv, tai_khoan, mat_khau, vai_tro) VALUES (%s,%s,%s,%s)",
            ("Quản trị viên", "admin", mk, "admin")
        )
        conn.commit()
        print("  Tài khoản admin tạo xong (admin / 123456)")


def _them_du_lieu_mau(cursor, conn):
    cursor.execute("SELECT COUNT(*) FROM loai_san_pham")
    if cursor.fetchone()[0] == 0:
        loai = [
            ("Bút viết",     "Bút bi, gel, chì, lông..."),
            ("Vở - Giấy",    "Vở, tập, giấy in, giấy note"),
            ("Mực in",       "Mực máy in, hộp mực các loại"),
            ("Dụng cụ VPP",  "Kéo, dập ghim, băng keo, ruler"),
            ("Văn phòng phẩm khác", "Các loại khác"),
        ]
        cursor.executemany(
            "INSERT INTO loai_san_pham (ten_loai, mo_ta) VALUES (%s, %s)", loai
        )
        conn.commit()
        print("  Thêm 5 loại sản phẩm mẫu")

    cursor.execute("SELECT COUNT(*) FROM san_pham")
    if cursor.fetchone()[0] == 0:
        sp = [
            ("VPP001", "Bút bi Thiên Long TL-027", 1, "cái", 3500, 5000, 200),
            ("VPP002", "Bút gel Thiên Long GEL-04",1, "cái", 6000, 8500, 150),
            ("VPP003", "Vở kẻ ngang 96 trang",    2, "quyển",8000,12000, 300),
            ("VPP004", "Giấy in A4 70gsm (500 tờ)",2, "ram", 65000,85000,  50),
            ("VPP005", "Hộp mực Canon PG-745",     3, "hộp", 85000,120000,  20),
            ("VPP006", "Kéo văn phòng Kengo",       4, "cái", 12000,20000,  80),
            ("VPP007", "Băng keo trong 24mm",       4, "cuộn",4500,  7000, 120),
        ]
        cursor.executemany("""
            INSERT INTO san_pham (ma_code, ten_sp, ma_loai, don_vi, gia_nhap, gia_ban, ton_kho)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, sp)
        conn.commit()
        print(" Thêm 7 sản phẩm mẫu")