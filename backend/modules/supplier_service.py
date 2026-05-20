from backend.database.connection import get_connection
from backend.models.supplier import Supplier


def get_all(keyword: str = "", only_active: bool = True) -> list:
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT
            ma_ncc,
            ten_ncc,
            COALESCE(nguoi_lh, ''),
            COALESCE(dia_chi, ''),
            COALESCE(so_dt, ''),
            COALESCE(email, ''),
            COALESCE(website, ''),
            COALESCE(ghi_chu, ''),
            COALESCE(trang_thai, 1)
        FROM nha_cung_cap
        WHERE 1=1
    """

    params = []

    if only_active:
        sql += " AND COALESCE(trang_thai,1)=1"

    if keyword:
        sql += """
            AND (
                ten_ncc LIKE %s
                OR so_dt LIKE %s
                OR email LIKE %s
            )
        """
        kw = f"%{keyword}%"
        params += [kw, kw, kw]

    sql += " ORDER BY ten_ncc"

    cur.execute(sql, params)

    result = [Supplier.from_row(r) for r in cur.fetchall()]

    conn.close()
    return result


def get_by_id(ma_ncc: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            ma_ncc,
            ten_ncc,
            COALESCE(nguoi_lh, ''),
            COALESCE(dia_chi, ''),
            COALESCE(so_dt, ''),
            COALESCE(email, ''),
            COALESCE(website, ''),
            COALESCE(ghi_chu, ''),
            COALESCE(trang_thai, 1)
        FROM nha_cung_cap
        WHERE ma_ncc=%s
    """, (ma_ncc,))

    row = cur.fetchone()

    conn.close()

    return Supplier.from_row(row) if row else None


def add(s: Supplier) -> tuple:
    if not s.ten_ncc:
        return False, "Tên NCC không được trống!"

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO nha_cung_cap
            (
                ten_ncc,
                nguoi_lh,
                dia_chi,
                so_dt,
                email,
                website,
                ghi_chu
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            s.ten_ncc,
            s.nguoi_lh,
            s.dia_chi,
            s.so_dt,
            s.email,
            s.website,
            s.ghi_chu
        ))

        conn.commit()

        return True, "Thêm nhà cung cấp thành công!"

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def update(s: Supplier) -> tuple:
    if not s.ten_ncc:
        return False, "Tên NCC không được trống!"

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE nha_cung_cap
            SET
                ten_ncc=%s,
                nguoi_lh=%s,
                dia_chi=%s,
                so_dt=%s,
                email=%s,
                website=%s,
                ghi_chu=%s
            WHERE ma_ncc=%s
        """, (
            s.ten_ncc,
            s.nguoi_lh,
            s.dia_chi,
            s.so_dt,
            s.email,
            s.website,
            s.ghi_chu,
            s.ma_ncc
        ))

        conn.commit()

        return True, "Cập nhật thành công!"

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def toggle_status(ma_ncc: int) -> tuple:
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT COALESCE(trang_thai,1) FROM nha_cung_cap WHERE ma_ncc=%s",
            (ma_ncc,)
        )

        row = cur.fetchone()

        if not row:
            return False, "Không tìm thấy nhà cung cấp!"

        current = int(row[0])

        # đảo trạng thái đúng
        new_st = 0 if current == 1 else 1

        cur.execute(
            "UPDATE nha_cung_cap SET trang_thai=%s WHERE ma_ncc=%s",
            (new_st, ma_ncc)
        )

        conn.commit()

        return True, "Đã cập nhật trạng thái!"

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()

def get_dropdown() -> list:
    """
    Lấy danh sách NCC hoạt động cho combobox.
    Return:
        [(ma_ncc, ten_ncc), ...]
    """

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT ma_ncc, ten_ncc
            FROM nha_cung_cap
            WHERE COALESCE(trang_thai, 1) = 1
            ORDER BY ten_ncc
        """)

        return cur.fetchall()

    finally:
        conn.close()