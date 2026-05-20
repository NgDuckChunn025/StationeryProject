# backend/modules/config_service.py
from backend.database.connection import get_connection


def get(key: str, default: str = "") -> str:
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT gia_tri FROM cau_hinh WHERE ten_khoa=%s", (key,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row and row[0] is not None else default
    except Exception:
        return default


def get_all() -> dict:
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT ten_khoa, gia_tri FROM cau_hinh")
        rows = cur.fetchall()
        conn.close()
        return {r[0]: (r[1] or "") for r in rows}
    except Exception:
        return {}


def set_val(key: str, value: str) -> bool:
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO cau_hinh (ten_khoa, gia_tri)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE gia_tri = VALUES(gia_tri)
        """, (key, value))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[config] {e}")
        return False


def get_int(key: str, default: int = 0) -> int:
    try:
        return int(get(key, str(default)))
    except Exception:
        return default


def get_store_info() -> dict:
    cfg = get_all()
    return {
        "ten_cua_hang" : cfg.get("ten_cua_hang",    "Cửa Hàng Văn Phòng Phẩm"),
        "dia_chi"      : cfg.get("dia_chi",          ""),
        "so_dien_thoai": cfg.get("so_dien_thoai",    ""),
        "email"        : cfg.get("email",             ""),
        "website"      : cfg.get("website",           ""),
    }
