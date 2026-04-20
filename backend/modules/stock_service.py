from backend.database.connection import get_connection


def stock_in(ma_sp, so_luong):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # thêm vào bảng nhập kho
        cursor.execute("""
            INSERT INTO nhap_kho (ma_sp, so_luong, gia_nhap)
            VALUES (%s, %s, 0)
        """, (ma_sp, so_luong))

        # cập nhật tồn kho
        cursor.execute("""
            UPDATE san_pham
            SET ton_kho = ton_kho + %s
            WHERE ma_sp = %s
        """, (so_luong, ma_sp))

        conn.commit()
        return True, "Nhập kho thành công"

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def get_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nk.ma_nhap, sp.ten_sp, nk.so_luong, nk.ngay_nhap
        FROM nhap_kho nk
        JOIN san_pham sp ON nk.ma_sp = sp.ma_sp
        ORDER BY nk.ma_nhap DESC
    """)

    data = cursor.fetchall()
    conn.close()
    return data