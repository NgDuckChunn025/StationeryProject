# backend/database/db_migrate.py — hoàn chỉnh, bao gồm tất cả tính năng mới
import mysql.connector
from mysql.connector import Error
from backend.database.connection import DB_CONFIG


def _col(cur, t, c):
    cur.execute("""SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s""",
        (DB_CONFIG["database"], t, c))
    return cur.fetchone()[0] > 0

def _tbl(cur, t):
    cur.execute("""SELECT COUNT(*) FROM information_schema.TABLES
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s""",
        (DB_CONFIG["database"], t))
    return cur.fetchone()[0] > 0

def _add(cur, conn, t, c, defn):
    if _tbl(cur, t) and not _col(cur, t, c):
        try:
            cur.execute(f"ALTER TABLE `{t}` ADD COLUMN `{c}` {defn}")
            conn.commit(); print(f"    + {t}.{c}")
        except Error as e:
            print(f"    ⚠ {t}.{c}: {e}")

def _mk(cur, conn, t, ddl):
    if not _tbl(cur, t):
        try:
            cur.execute(ddl); conn.commit()
            print(f"    + Tạo bảng {t}")
        except Error as e:
            print(f"    ⚠ {t}: {e}")


def chay_migration() -> bool:
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur  = conn.cursor()
        print("  🔄 Kiểm tra migration...")

        # Bảng thiếu
        _mk(cur,conn,"nha_cung_cap","""CREATE TABLE nha_cung_cap(
            ma_ncc INT AUTO_INCREMENT PRIMARY KEY, ten_ncc VARCHAR(200) NOT NULL,
            nguoi_lh VARCHAR(100), dia_chi VARCHAR(300), so_dt VARCHAR(20),
            email VARCHAR(100), website VARCHAR(200), ghi_chu TEXT,
            trang_thai TINYINT(1) DEFAULT 1,
            ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        _mk(cur,conn,"phieu_nhap","""CREATE TABLE phieu_nhap(
            ma_phieu INT AUTO_INCREMENT PRIMARY KEY, ma_ncc INT, ma_nv INT,
            ngay_nhap DATETIME DEFAULT CURRENT_TIMESTAMP,
            tong_tien DECIMAL(15,0) DEFAULT 0, da_thanh_toan TINYINT(1) DEFAULT 0,
            ghi_chu TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        _mk(cur,conn,"chi_tiet_phieu_nhap","""CREATE TABLE chi_tiet_phieu_nhap(
            ma_ct INT AUTO_INCREMENT PRIMARY KEY, ma_phieu INT NOT NULL,
            ma_sp INT NOT NULL, so_luong INT DEFAULT 1,
            don_gia DECIMAL(15,0) DEFAULT 0, han_su_dung DATE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        _mk(cur,conn,"phieu_tra_hang","""CREATE TABLE phieu_tra_hang(
            ma_phieu_tra INT AUTO_INCREMENT PRIMARY KEY,
            ma_hd_goc INT NOT NULL, ma_nv INT NOT NULL,
            ngay_tra DATETIME DEFAULT CURRENT_TIMESTAMP,
            ly_do VARCHAR(300), tong_hoan DECIMAL(15,0) DEFAULT 0,
            hinh_thuc_hoan VARCHAR(50) DEFAULT 'Tiền mặt', ghi_chu TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        _mk(cur,conn,"chi_tiet_phieu_tra","""CREATE TABLE chi_tiet_phieu_tra(
            ma_ct INT AUTO_INCREMENT PRIMARY KEY,
            ma_phieu_tra INT NOT NULL, ma_sp INT NOT NULL,
            so_luong_tra INT DEFAULT 1, don_gia DECIMAL(15,0) DEFAULT 0,
            ly_do_chi VARCHAR(200)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        _mk(cur,conn,"cau_hinh","""CREATE TABLE cau_hinh(
            ma_ch INT AUTO_INCREMENT PRIMARY KEY,
            ten_khoa VARCHAR(100) UNIQUE NOT NULL,
            gia_tri TEXT, mo_ta VARCHAR(255),
            ngay_capnhat DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        _mk(cur,conn,"nhat_ky_hoat_dong","""CREATE TABLE nhat_ky_hoat_dong(
            ma_log INT AUTO_INCREMENT PRIMARY KEY,
            ma_nv INT, ten_nv VARCHAR(200),
            hanh_dong VARCHAR(100) NOT NULL,
            mo_ta TEXT, doi_tuong VARCHAR(50),
            ma_doi_tuong INT,
            thoi_gian DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

        # Cột thiếu
        for c,d in [("mo_ta","TEXT"),("ton_kho_min","INT DEFAULT 10"),
                    ("trang_thai","TINYINT(1) DEFAULT 1"),
                    ("hinh_anh","VARCHAR(500)"),
                    ("ma_loai","INT"),
                    ("ngay_tao","DATETIME DEFAULT CURRENT_TIMESTAMP")]:
            _add(cur,conn,"san_pham",c,d)
        for c,d in [("ngay_ban","DATETIME DEFAULT CURRENT_TIMESTAMP"),
                    ("ghi_chu","TEXT"),("trang_thai","VARCHAR(20) DEFAULT 'Hoàn thành'"),
                    ("tong_tien","DECIMAL(15,0) DEFAULT 0"),
                    ("giam_gia","DECIMAL(15,0) DEFAULT 0"),
                    ("thanh_toan","DECIMAL(15,0) DEFAULT 0"),
                    ("hinh_thuc","VARCHAR(50) DEFAULT 'Tiền mặt'"),
                    ("ma_nv","INT"),("ma_kh","INT")]:
            _add(cur,conn,"hoa_don",c,d)
        for c,d in [("don_gia","DECIMAL(15,0) DEFAULT 0"),
                    ("so_luong","INT DEFAULT 1"),
                    ("ma_sp","INT"),("ma_hd","INT")]:
            _add(cur,conn,"chi_tiet_hoa_don",c,d)
        for c,d in [("email","VARCHAR(100)"),("ngay_sinh","DATE"),
                    ("gioi_tinh","TINYINT(1)"),
                    ("diem_tich_luy","INT DEFAULT 0"),
                    ("hang_khach_hang","VARCHAR(20) DEFAULT 'Thường'"),
                    ("tong_chi_tieu","DECIMAL(15,0) DEFAULT 0"),
                    ("ngay_tao","DATETIME DEFAULT CURRENT_TIMESTAMP")]:
            _add(cur,conn,"khach_hang",c,d)
        for c,d in [("so_dt","VARCHAR(20)"),("email","VARCHAR(100)"),
                    ("dia_chi","VARCHAR(300)"),("ngay_vao","DATE"),
                    ("trang_thai","TINYINT(1) DEFAULT 1"),
                    ("vai_tro","VARCHAR(20) DEFAULT 'nhanvien'")]:
            _add(cur,conn,"nhan_vien",c,d)

        # Cấu hình mặc định
        cur.execute("SELECT COUNT(*) FROM cau_hinh")
        if cur.fetchone()[0] == 0:
            cur.executemany("""
                INSERT IGNORE INTO cau_hinh (ten_khoa,gia_tri,mo_ta)
                VALUES (%s,%s,%s)""", [
                ("ten_cua_hang",    "Cửa Hàng Văn Phòng Phẩm", "Tên cửa hàng"),
                ("dia_chi",         "123 Đường ABC, TP.HCM",    "Địa chỉ"),
                ("so_dien_thoai",   "028 1234 5678",             "Điện thoại"),
                ("email",           "",                          "Email"),
                ("website",         "",                          "Website"),
                ("ma_so_thue",      "",                          "MST"),
                ("ty_le_tich_diem", "10000",  "Tiền/1 điểm"),
                ("doi_diem",        "1000",   "1 điểm = N đồng giảm"),
                ("canh_bao_ton_kho","10",     "Ngưỡng cảnh báo tồn kho"),
                ("nguong_hang_bac",    "500000",  "Ngưỡng hạng Bạc"),
                ("nguong_hang_vang",   "2000000", "Ngưỡng hạng Vàng"),
                ("nguong_hang_bachkim","5000000", "Ngưỡng hạng Bạch Kim"),
            ])
            conn.commit(); print("    + Config mặc định")

        # Fix NULL
        cur.execute("UPDATE san_pham SET trang_thai=1 WHERE trang_thai IS NULL")
        conn.commit()

        cur.close(); conn.close()
        print("  ✅ Migration hoàn tất\n"); return True
    except Error as e:
        print(f"  ❌ Migration lỗi: {e}"); return False
