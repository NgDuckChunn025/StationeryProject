# backend/modules/customer_service.py

from backend.database.connection import get_connection


def get_all(keyword=""):
    conn = get_connection()
    cursor = conn.cursor()

    if keyword:
        kw = f"%{keyword}%"
        cursor.execute("""
            SELECT ma_kh, ten_kh, so_dt, dia_chi, diem_tich_luy
            FROM khach_hang
            WHERE ten_kh LIKE %s OR so_dt LIKE %s
            ORDER BY ten_kh
        """, (kw, kw))
    else:
        cursor.execute("""
            SELECT ma_kh, ten_kh, so_dt, dia_chi, diem_tich_luy
            FROM khach_hang
            ORDER BY ten_kh
        """)

    rows = cursor.fetchall()
    conn.close()
    return rows