# main.py
# ================================================================
# Điểm khởi chạy ứng dụng VPP Manager
# Luồng: MySQL → tao_database → migration → đăng nhập → cửa sổ chính
# ================================================================

import sys
import customtkinter as ctk
from tkinter import messagebox

from backend.database.connection import test_connection
from backend.database.db_init       import tao_database
from backend.database.db_migrate    import chay_migration
from backend.database.db_migrate_fk import chay_migration_fk
from frontend.gui.login_ui   import LoginWindow
from frontend.gui.main_window import MainWindow


def main():
    print("=" * 54)
    print("   VPP Manager — Khởi động")
    print("=" * 54)

    # ── 1. Kiểm tra kết nối MySQL ──────────────────────────
    print("\n[1/4] Kiểm tra kết nối MySQL...")
    if not test_connection():
        _root = ctk.CTk(); _root.withdraw()
        messagebox.showerror(
            "Lỗi kết nối MySQL",
            "Không thể kết nối tới MySQL!\n\n"
            "Kiểm tra:\n"
            "  • MySQL Server đang chạy\n"
            "  • Thông tin trong backend/database/connection.py\n"
            "    (host, port, user, password)"
        )
        _root.destroy(); sys.exit(1)
    print("     ✅ Kết nối thành công")

    # ── 2. Tạo database & bảng (nếu chưa có) ──────────────
    print("\n[2/4] Khởi tạo database...")
    if not tao_database():
        _root = ctk.CTk(); _root.withdraw()
        messagebox.showerror(
            "Lỗi database",
            "Không thể tạo database.\nXem chi tiết trong terminal."
        )
        _root.destroy(); sys.exit(1)

    # ── 3. Migration: thêm cột/bảng còn thiếu ─────────────
    print("[3/5] Kiểm tra & cập nhật cấu trúc database...")
    chay_migration()   # Không exit khi lỗi — chỉ cảnh báo

    # ── 4. Migration FK: bổ sung ràng buộc khoá ngoại ─────
    print("[4/5] Bổ sung Foreign Key constraints...")
    chay_migration_fk()   # Không exit khi lỗi — chỉ cảnh báo

    # ── 5. Giao diện ───────────────────────────────────────
    print("[5/5] Mở giao diện...\n")
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    login = LoginWindow()
    login.mainloop()

    if login.user_info:
        app = MainWindow(login.user_info)
        app.mainloop()

    print("\n  Ứng dụng đã đóng. Tạm biệt!")


if __name__ == "__main__":
    main()