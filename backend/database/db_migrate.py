# backend/database/db_migrate.py
# ================================================================
# Migration an toàn: CREATE TABLE IF NOT EXISTS + ALTER TABLE
# Chạy mỗi lần khởi động — không bao giờ xóa dữ liệu
# ================================================================

import mysql.connector
from mysql.connector import Error
from backend.database.connection import DB_CONFIG


def _col_exists(cursor, table: str, col: str) -> bool:
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s
    """, (DB_CONFIG["database"], table, col))
    return cursor.fetchone()[0] > 0


def _table_exists(cursor, table: str) -> bool:
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.TABLES
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
    """, (DB_CONFIG["database"], table))
    return cursor.fetchone()[0] > 0


def _add_col(cursor, conn, table: str, col: str, definition: str):
    if not _table_exists(cursor, table):
        return  # bảng chưa tồn tại, bỏ qua
    if not _col_exists(cursor, table, col):
        try:
            cursor.execute(
                f"ALTER TABLE `{table}` ADD COLUMN `{col}` {definition}")
            conn.commit()
            print(f"    + {table}.{col}")
        except Error as e:
            print(f"    ⚠ {table}.{col}: {e}")


def _create_table(cursor, conn, table: str, ddl: str):
    """Tạo bảng nếu chưa tồn tại."""
    if not _table_exists(cursor, table):
        try:
            cursor.execute(ddl)
            conn.commit()
            print(f"    + Tạo bảng {table}")
        except Error as e:
            print(f"    ⚠ Tạo {table}: {e}")


def chay_migration() -> bool:
    try:
        conn   = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("  🔄 Kiểm tra & cập nhật cấu trúc database...")

        # ── Bước 1: Tạo bảng còn thiếu ─────────────────────
        _create_table(cursor, conn, "nha_cung_cap", """
            CREATE TABLE nha_cung_cap (
                ma_ncc   INT AUTO_INCREMENT PRIMARY KEY,
                ten_ncc  VARCHAR(200) NOT NULL,
                nguoi_lh VARCHAR(100),
                dia_chi  VARCHAR(300),
                so_dt    VARCHAR(20),
                email    VARCHAR(100),
                website  VARCHAR(200),
                ghi_chu  TEXT,
                trang_thai TINYINT(1) DEFAULT 1,
                ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        _create_table(cursor, conn, "phieu_nhap", """
            CREATE TABLE phieu_nhap (
                ma_phieu     INT AUTO_INCREMENT PRIMARY KEY,
                ma_ncc       INT,
                ma_nv        INT,
                ngay_nhap    DATETIME DEFAULT CURRENT_TIMESTAMP,
                tong_tien    DECIMAL(15,0) DEFAULT 0,
                da_thanh_toan TINYINT(1) DEFAULT 0,
                ghi_chu      TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        _create_table(cursor, conn, "chi_tiet_phieu_nhap", """
            CREATE TABLE chi_tiet_phieu_nhap (
                ma_ct    INT AUTO_INCREMENT PRIMARY KEY,
                ma_phieu INT NOT NULL,
                ma_sp    INT NOT NULL,
                so_luong INT DEFAULT 1,
                don_gia  DECIMAL(15,0) DEFAULT 0,
                han_su_dung DATE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        _create_table(cursor, conn, "phieu_tra_hang", """
            CREATE TABLE phieu_tra_hang (
                ma_phieu_tra   INT AUTO_INCREMENT PRIMARY KEY,
                ma_hd_goc      INT NOT NULL,
                ma_nv          INT NOT NULL,
                ngay_tra       DATETIME DEFAULT CURRENT_TIMESTAMP,
                ly_do          VARCHAR(300),
                tong_hoan      DECIMAL(15,0) DEFAULT 0,
                hinh_thuc_hoan VARCHAR(50) DEFAULT 'Tiền mặt',
                ghi_chu        TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        _create_table(cursor, conn, "chi_tiet_phieu_tra", """
            CREATE TABLE chi_tiet_phieu_tra (
                ma_ct        INT AUTO_INCREMENT PRIMARY KEY,
                ma_phieu_tra INT NOT NULL,
                ma_sp        INT NOT NULL,
                so_luong_tra INT DEFAULT 1,
                don_gia      DECIMAL(15,0) DEFAULT 0,
                ly_do_chi    VARCHAR(200)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        _create_table(cursor, conn, "lich_su_diem_kh", """
            CREATE TABLE lich_su_diem_kh (
                ma_ls    INT AUTO_INCREMENT PRIMARY KEY,
                ma_kh    INT NOT NULL,
                loai     VARCHAR(20) NOT NULL,
                so_diem  INT NOT NULL,
                ly_do    VARCHAR(200),
                ma_hd    INT,
                ngay_ghi DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        _create_table(cursor, conn, "cau_hinh", """
            CREATE TABLE cau_hinh (
                ma_ch        INT AUTO_INCREMENT PRIMARY KEY,
                ten_khoa     VARCHAR(100) UNIQUE NOT NULL,
                gia_tri      TEXT,
                mo_ta        VARCHAR(255),
                ngay_capnhat DATETIME DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── Bước 2: Thêm cột còn thiếu vào bảng hiện có ────

        # san_pham
        _add_col(cursor, conn, "san_pham", "mo_ta",
                 "TEXT")
        _add_col(cursor, conn, "san_pham", "ton_kho_min",
                 "INT DEFAULT 10")
        _add_col(cursor, conn, "san_pham", "trang_thai",
                 "TINYINT(1) DEFAULT 1")
        _add_col(cursor, conn, "san_pham", "hinh_anh",
                 "VARCHAR(500) DEFAULT NULL")
        _add_col(cursor, conn, "san_pham", "ma_loai",
                 "INT")
        _add_col(cursor, conn, "san_pham", "ngay_tao",
                 "DATETIME DEFAULT CURRENT_TIMESTAMP")

        # hoa_don
        _add_col(cursor, conn, "hoa_don", "ngay_ban",
                 "DATETIME DEFAULT CURRENT_TIMESTAMP")
        _add_col(cursor, conn, "hoa_don", "ghi_chu",
                 "TEXT")
        _add_col(cursor, conn, "hoa_don", "trang_thai",
                 "VARCHAR(20) DEFAULT 'Hoàn thành'")
        _add_col(cursor, conn, "hoa_don", "tong_tien",
                 "DECIMAL(15,0) DEFAULT 0")
        _add_col(cursor, conn, "hoa_don", "giam_gia",
                 "DECIMAL(15,0) DEFAULT 0")
        _add_col(cursor, conn, "hoa_don", "thanh_toan",
                 "DECIMAL(15,0) DEFAULT 0")
        _add_col(cursor, conn, "hoa_don", "hinh_thuc",
                 "VARCHAR(50) DEFAULT 'Tiền mặt'")
        _add_col(cursor, conn, "hoa_don", "ma_nv", "INT")
        _add_col(cursor, conn, "hoa_don", "ma_kh", "INT")

        # chi_tiet_hoa_don
        _add_col(cursor, conn, "chi_tiet_hoa_don", "ghi_chu",
                 "VARCHAR(200)")
        _add_col(cursor, conn, "chi_tiet_hoa_don", "don_gia",
                 "DECIMAL(15,0) DEFAULT 0")
        _add_col(cursor, conn, "chi_tiet_hoa_don", "so_luong",
                 "INT DEFAULT 1")
        _add_col(cursor, conn, "chi_tiet_hoa_don", "ma_sp", "INT")
        _add_col(cursor, conn, "chi_tiet_hoa_don", "ma_hd", "INT")

        # khach_hang
        _add_col(cursor, conn, "khach_hang", "email",
                 "VARCHAR(100)")
        _add_col(cursor, conn, "khach_hang", "ngay_sinh", "DATE")
        _add_col(cursor, conn, "khach_hang", "gioi_tinh", "TINYINT(1)")
        _add_col(cursor, conn, "khach_hang", "diem_tich_luy",
                 "INT DEFAULT 0")
        _add_col(cursor, conn, "khach_hang", "hang_khach_hang",
                 "VARCHAR(20) DEFAULT 'Thường'")
        _add_col(cursor, conn, "khach_hang", "tong_chi_tieu",
                 "DECIMAL(15,0) DEFAULT 0")
        _add_col(cursor, conn, "khach_hang", "ngay_tao",
                 "DATETIME DEFAULT CURRENT_TIMESTAMP")

        # nhan_vien
        _add_col(cursor, conn, "nhan_vien", "so_dt",     "VARCHAR(20)")
        _add_col(cursor, conn, "nhan_vien", "email",     "VARCHAR(100)")
        _add_col(cursor, conn, "nhan_vien", "dia_chi",   "VARCHAR(300)")
        _add_col(cursor, conn, "nhan_vien", "ngay_vao",  "DATE")
        _add_col(cursor, conn, "nhan_vien", "trang_thai","TINYINT(1) DEFAULT 1")
        _add_col(cursor, conn, "nhan_vien", "vai_tro",
                 "VARCHAR(20) DEFAULT 'nhanvien'")

        # nha_cung_cap
        _add_col(cursor, conn, "nha_cung_cap", "nguoi_lh",  "VARCHAR(100)")
        _add_col(cursor, conn, "nha_cung_cap", "website",   "VARCHAR(200)")
        _add_col(cursor, conn, "nha_cung_cap", "ghi_chu",   "TEXT")
        _add_col(cursor, conn, "nha_cung_cap", "trang_thai","TINYINT(1) DEFAULT 1")
        _add_col(cursor, conn, "nha_cung_cap", "ngay_tao",
                 "DATETIME DEFAULT CURRENT_TIMESTAMP")

        # phieu_nhap
        _add_col(cursor, conn, "phieu_nhap", "da_thanh_toan",
                 "TINYINT(1) DEFAULT 0")
        _add_col(cursor, conn, "phieu_nhap", "ngay_nhap",
                 "DATETIME DEFAULT CURRENT_TIMESTAMP")

        # chi_tiet_phieu_nhap
        _add_col(cursor, conn, "chi_tiet_phieu_nhap",
                 "han_su_dung", "DATE")

        # ── Bước 3: Cấu hình mặc định ───────────────────────
        cursor.execute("SELECT COUNT(*) FROM cau_hinh")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT IGNORE INTO cau_hinh (ten_khoa, gia_tri, mo_ta)
                VALUES (%s, %s, %s)
            """, [
                ("ten_cua_hang",    "Cửa Hàng VPP",   "Tên trên hóa đơn"),
                ("dia_chi",         "123 Đường ABC",   "Địa chỉ"),
                ("so_dien_thoai",   "028 1234 5678",   "SĐT"),
                ("email",           "",                 "Email"),
                ("website",         "",                 "Website"),
                ("ty_le_tich_diem", "10000",            "Tiền/1 điểm"),
                ("canh_bao_ton_kho","10",               "Ngưỡng tồn kho"),
            ])
            conn.commit()
            print("    + Thêm cấu hình mặc định")

        # ── Bước 4: Fix dữ liệu NULL ────────────────────────
        cursor.execute(
            "UPDATE san_pham SET trang_thai=1 WHERE trang_thai IS NULL")
        conn.commit()

        cursor.close()
        conn.close()
        print("  ✅ Migration hoàn tất\n")
        return True

    except Error as e:
        print(f"  ❌ Lỗi migration: {e}")
        return False
