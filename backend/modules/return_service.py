# backend/modules/return_service.py
# ================================================================
# Nghiệp vụ trả hàng: tạo phiếu trả, hoàn tồn kho, trả điểm
# ================================================================
from backend.database.connection import get_connection


def get_invoice_for_return(ma_hd: int) -> dict | None:
    """Lấy hóa đơn và chi tiết để làm phiếu trả."""
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT hd.ma_hd, hd.ma_kh,
                   COALESCE(kh.ten_kh,'Khách lẻ') AS ten_kh,
                   hd.thanh_toan, hd.trang_thai
            FROM hoa_don hd
            LEFT JOIN khach_hang kh ON hd.ma_kh = kh.ma_kh
            WHERE hd.ma_hd = %s
        """, (ma_hd,))
        hd = cur.fetchone()
        if not hd:
            return None

        cur.execute("""
            SELECT ct.ma_sp, sp.ten_sp, ct.don_gia,
                   ct.so_luong, ct.don_gia * ct.so_luong AS thanh_tien
            FROM chi_tiet_hoa_don ct
            JOIN san_pham sp ON ct.ma_sp = sp.ma_sp
            WHERE ct.ma_hd = %s
        """, (ma_hd,))
        items = cur.fetchall()

        return {
            "ma_hd"    : hd[0],
            "ma_kh"    : hd[1],
            "ten_kh"   : hd[2],
            "thanh_toan": float(hd[3] or 0),
            "trang_thai": hd[4],
            "items"    : [
                {"ma_sp": r[0], "ten_sp": r[1],
                 "don_gia": float(r[2] or 0),
                 "so_luong": r[3],
                 "thanh_tien": float(r[4] or 0)}
                for r in items
            ],
        }
    except Exception as e:
        print(f"[return_service] {e}")
        return None
    finally:
        conn.close()


def create_return(ma_hd_goc: int, ma_nv: int,
                  items_tra: list, ly_do: str,
                  hinh_thuc_hoan: str = "Tiền mặt") -> tuple:
    """
    Tạo phiếu trả hàng.
    items_tra = [{"ma_sp": int, "so_luong_tra": int, "don_gia": float}, ...]
    Trả về (True, ma_phieu_tra) hoặc (False, lỗi).
    """
    if not items_tra:
        return False, "Chưa chọn sản phẩm cần trả!"

    tong_hoan = sum(i["so_luong_tra"] * i["don_gia"]
                    for i in items_tra)
    conn = get_connection()
    cur  = conn.cursor()
    try:
        # Tạo phiếu trả
        cur.execute("""
            INSERT INTO phieu_tra_hang
                (ma_hd_goc, ma_nv, ly_do, tong_hoan, hinh_thuc_hoan)
            VALUES (%s, %s, %s, %s, %s)
        """, (ma_hd_goc, ma_nv, ly_do, tong_hoan, hinh_thuc_hoan))
        ma_phieu = cur.lastrowid

        for item in items_tra:
            cur.execute("""
                INSERT INTO chi_tiet_phieu_tra
                    (ma_phieu_tra, ma_sp, so_luong_tra, don_gia)
                VALUES (%s, %s, %s, %s)
            """, (ma_phieu, item["ma_sp"],
                  item["so_luong_tra"], item["don_gia"]))
            # Hoàn tồn kho
            cur.execute("""
                UPDATE san_pham
                SET ton_kho = ton_kho + %s
                WHERE ma_sp = %s
            """, (item["so_luong_tra"], item["ma_sp"]))

        # Lấy ma_kh từ hóa đơn gốc để trừ điểm
        cur.execute("SELECT ma_kh, thanh_toan FROM hoa_don WHERE ma_hd=%s",
                    (ma_hd_goc,))
        hd_row = cur.fetchone()
        if hd_row and hd_row[0]:
            ma_kh = hd_row[0]
            # Trừ điểm tương ứng số tiền hoàn
            try:
                from backend.modules.config_service import get_int
                ty_le = get_int("ty_le_tich_diem", 10000)
            except Exception:
                ty_le = 10000
            diem_tru = int(tong_hoan // ty_le)
            if diem_tru > 0:
                cur.execute("""
                    UPDATE khach_hang
                    SET diem_tich_luy = GREATEST(0, diem_tich_luy - %s),
                        tong_chi_tieu = GREATEST(0, tong_chi_tieu - %s)
                    WHERE ma_kh = %s
                """, (diem_tru, tong_hoan, ma_kh))

        conn.commit()
        return True, ma_phieu
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_return_history(limit: int = 50) -> list:
    """Lịch sử phiếu trả hàng."""
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT pt.ma_phieu_tra, pt.ma_hd_goc,
                   COALESCE(kh.ten_kh,'Khách lẻ'),
                   nv.ten_nv, pt.ngay_tra,
                   pt.tong_hoan, pt.ly_do, pt.hinh_thuc_hoan
            FROM phieu_tra_hang pt
            LEFT JOIN hoa_don hd ON pt.ma_hd_goc = hd.ma_hd
            LEFT JOIN khach_hang kh ON hd.ma_kh = kh.ma_kh
            LEFT JOIN nhan_vien nv ON pt.ma_nv = nv.ma_nv
            ORDER BY pt.ngay_tra DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()
    except Exception:
        return []
    finally:
        conn.close()
