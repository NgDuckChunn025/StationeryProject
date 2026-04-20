import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from tkinter import messagebox

from backend.database.connection import test_connection
from backend.database.db_init import tao_database
from frontend.gui.login_ui import LoginWindow
from frontend.gui.main_window import MainWindow


def main():
    print("=" * 52)
    print("  VPP Manager — Khởi động")
    print("=" * 52)

    print("\n[1/3] Kết nối MySQL...")
    if not test_connection():
        messagebox.showerror("Lỗi MySQL", "Không kết nối được MySQL!")
        return

    print("[2/3] Khởi tạo database...")
    tao_database()

    print("[3/3] Mở giao diện...\n")

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # 👉 tạo login trước
    login = LoginWindow()
    login.mainloop()

    # 👉 chỉ mở main nếu login OK
    if not login.user_info:
        print("Đăng nhập thất bại / thoát")
        return

    # 👉 quan trọng: destroy login trước khi mở main
    app = MainWindow(login.user_info)
    app.mainloop()


if __name__ == "__main__":
    main()