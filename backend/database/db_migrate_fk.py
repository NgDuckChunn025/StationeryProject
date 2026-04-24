# backend/database/db_migrate_fk.py
# ================================================================
# Thêm Foreign Key constraints còn thiếu vào DB hiện có.
# An toàn: kiểm tra trước khi thêm, không bao giờ xóa dữ liệu.
# Gọi sau chay_migration() trong main.py.
# ================================================================

import mysql.connector
from mysql.connector import Error
from backend.database.connection import DB_CONFIG


def _fk_exists(cursor, table: str, constraint_name: str) -> bool:
    """Kiểm tra một FK constraint đã tồn tại chưa."""
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA    = %s
          AND TABLE_NAME      = %s
          AND CONSTRAINT_NAME = %s
          AND CONSTRAINT_TYPE = 'FOREIGN KEY'
    """, (DB_CONFIG["database"], table, constraint_name))
    return cursor.fetchone()[0] > 0


def _add_fk(cursor, conn, table: str, constraint: str, definition: str):
    """Thêm FK nếu chưa tồn tại, bỏ qua nếu đã có."""
    if _fk_exists(cursor, table, constraint):
        return
    try:
        cursor.execute(
            f"ALTER TABLE `{table}` ADD CONSTRAINT `{constraint}` {definition}"
        )
        conn.commit()
        print(f"    + FK: {table}.{constraint}")
    except Error as e:
        # 1215 = Cannot add FK constraint (có thể do data orphan)
        if e.errno == 1215:
            print(f"    ! Bỏ qua {table}.{constraint} — có dữ liệu không hợp lệ: {e}")
        else:
            print(f"    ! Lỗi {table}.{constraint}: {e}")


def _clean_orphans(cursor, conn):
    """
    Xử lý dữ liệu mồ côi (orphan) nhẹ nhàng:
    SET NULL thay vì DELETE để không mất dữ liệu kinh doanh.
    """
    fixes = [
        # hoa_don.ma_kh trỏ về khách hàng không tồn tại -> NULL (khách lẻ)
        ("UPDATE hoa_don hd "
         "LEFT JOIN khach_hang kh ON hd.ma_kh = kh.ma_kh "
         "SET hd.ma_kh = NULL "
         "WHERE hd.ma_kh IS NOT NULL AND kh.ma_kh IS NULL"),

        # phieu_nhap.ma_ncc trỏ về NCC không tồn tại -> NULL
        ("UPDATE phieu_nhap pn "
         "LEFT JOIN nha_cung_cap ncc ON pn.ma_ncc = ncc.ma_ncc "
         "SET pn.ma_ncc = NULL "
         "WHERE pn.ma_ncc IS NOT NULL AND ncc.ma_ncc IS NULL"),

        # lich_su_diem_kh.ma_hd trỏ về hóa đơn không tồn tại -> NULL
        ("UPDATE lich_su_diem_kh ls "
         "LEFT JOIN hoa_don hd ON ls.ma_hd = hd.ma_hd "
         "SET ls.ma_hd = NULL "
         "WHERE ls.ma_hd IS NOT NULL AND hd.ma_hd IS NULL"),
    ]
    for sql in fixes:
        try:
            cursor.execute(sql)
            if cursor.rowcount:
                print(f"    ~ Dọn {cursor.rowcount} dòng orphan")
            conn.commit()
        except Error as e:
            print(f"    ! Lỗi dọn orphan: {e}")


def chay_migration_fk() -> bool:
    """
    Thêm toàn bộ FK constraints còn thiếu.
    Trả True nếu hoàn tất (kể cả khi có FK bị bỏ qua do orphan data).
    """
    try:
        conn   = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("  Kiểm tra & bổ sung Foreign Key constraints...")

        # Bước 1: Dọn dữ liệu mồ côi nhẹ nhàng trước
        _clean_orphans(cursor, conn)

        # Bước 2: Thêm các FK còn thiếu
        # ── hoa_don ─────────────────────────────────────────────
        _add_fk(cursor, conn,
                "hoa_don", "fk_hoadon_khachhang",
                "FOREIGN KEY (ma_kh) REFERENCES khach_hang(ma_kh) "
                "ON DELETE SET NULL ON UPDATE CASCADE")

        # ── phieu_nhap ──────────────────────────────────────────
        _add_fk(cursor, conn,
                "phieu_nhap", "fk_phieunhap_nhacungcap",
                "FOREIGN KEY (ma_ncc) REFERENCES nha_cung_cap(ma_ncc) "
                "ON DELETE SET NULL ON UPDATE CASCADE")

        _add_fk(cursor, conn,
                "phieu_nhap", "fk_phieunhap_nhanvien",
                "FOREIGN KEY (ma_nv) REFERENCES nhan_vien(ma_nv) "
                "ON DELETE SET NULL ON UPDATE CASCADE")

        # ── chi_tiet_phieu_nhap ─────────────────────────────────
        _add_fk(cursor, conn,
                "chi_tiet_phieu_nhap", "fk_ctpn_phieunhap",
                "FOREIGN KEY (ma_phieu) REFERENCES phieu_nhap(ma_phieu) "
                "ON DELETE CASCADE ON UPDATE CASCADE")

        _add_fk(cursor, conn,
                "chi_tiet_phieu_nhap", "fk_ctpn_sanpham",
                "FOREIGN KEY (ma_sp) REFERENCES san_pham(ma_sp) "
                "ON DELETE RESTRICT ON UPDATE CASCADE")

        # ── phieu_tra_hang ──────────────────────────────────────
        _add_fk(cursor, conn,
                "phieu_tra_hang", "fk_phieutra_hoadon",
                "FOREIGN KEY (ma_hd_goc) REFERENCES hoa_don(ma_hd) "
                "ON DELETE RESTRICT ON UPDATE CASCADE")

        _add_fk(cursor, conn,
                "phieu_tra_hang", "fk_phieutra_nhanvien",
                "FOREIGN KEY (ma_nv) REFERENCES nhan_vien(ma_nv) "
                "ON DELETE RESTRICT ON UPDATE CASCADE")

        # ── chi_tiet_phieu_tra ──────────────────────────────────
        _add_fk(cursor, conn,
                "chi_tiet_phieu_tra", "fk_ctpt_phieutra",
                "FOREIGN KEY (ma_phieu_tra) REFERENCES phieu_tra_hang(ma_phieu_tra) "
                "ON DELETE CASCADE ON UPDATE CASCADE")

        _add_fk(cursor, conn,
                "chi_tiet_phieu_tra", "fk_ctpt_sanpham",
                "FOREIGN KEY (ma_sp) REFERENCES san_pham(ma_sp) "
                "ON DELETE RESTRICT ON UPDATE CASCADE")

        # ── lich_su_diem_kh ─────────────────────────────────────
        _add_fk(cursor, conn,
                "lich_su_diem_kh", "fk_lsdiem_khachhang",
                "FOREIGN KEY (ma_kh) REFERENCES khach_hang(ma_kh) "
                "ON DELETE CASCADE ON UPDATE CASCADE")

        _add_fk(cursor, conn,
                "lich_su_diem_kh", "fk_lsdiem_hoadon",
                "FOREIGN KEY (ma_hd) REFERENCES hoa_don(ma_hd) "
                "ON DELETE SET NULL ON UPDATE CASCADE")

        cursor.close()
        conn.close()
        print("  FK migration hoàn tất\n")
        return True

    except Error as e:
        print(f"  Lỗi FK migration: {e}")
        return False