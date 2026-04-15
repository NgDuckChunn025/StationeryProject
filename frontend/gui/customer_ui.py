# frontend/gui/customer_ui.py
# ================================================================
# Màn hình Quản lý Khách hàng (CRUD đầy đủ + UI đẹp)
# ================================================================

import customtkinter as ctk
from tkinter import ttk, messagebox
from backend.database.connection import get_connection

style = ttk.Style()
style.theme_use("default")

style.configure(
    "Treeview",
    font=("Segoe UI", 12),
    rowheight=32
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 13, "bold")
)

class CustomerFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build_ui()
        self._load()

    # ============================================================
    # UI
    # ============================================================
    def _build_ui(self):
        # TITLE
        ctk.CTkLabel(
            self,
            text="QUẢN LÝ KHÁCH HÀNG",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=20, pady=(16, 10))

        # TOOLBAR
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=20, pady=6)

        ctk.CTkButton(tb, text="+ Thêm", width=110,
                      command=self._add).pack(side="right", padx=4)

        ctk.CTkButton(tb, text="Sửa", width=100,
                      fg_color="#E65100",
                      command=self._edit).pack(side="right", padx=4)

        ctk.CTkButton(tb, text="Xóa", width=100,
                      fg_color="#C62828",
                      command=self._delete).pack(side="right")

        # SEARCH
        sb = ctk.CTkFrame(self, fg_color="transparent")
        sb.pack(fill="x", padx=20, pady=(0, 10))

        self.ent_search = ctk.CTkEntry(
            sb, height=38,
            placeholder_text="Tìm tên hoặc số điện thoại..."
        )
        self.ent_search.pack(side="left")
        self.ent_search.bind("<KeyRelease>", lambda _: self._load())

        self.lbl_count = ctk.CTkLabel(sb, text="", text_color="gray")
        self.lbl_count.pack(side="left", padx=10)

        # TABLE
        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Mã KH", "Tên", "SĐT", "Địa chỉ")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings")

        widths = [80, 220, 140, 260]

        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        scrollbar = ttk.Scrollbar(frm, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda _: self._edit())

    # ============================================================
    # DATA
    # ============================================================
    def _load(self):
        kw = self.ent_search.get().strip()

        conn = get_connection()
        cursor = conn.cursor()

        if kw:
            cursor.execute("""
                SELECT ma_kh, ten_kh, so_dt, dia_chi
                FROM khach_hang
                WHERE ten_kh LIKE %s OR so_dt LIKE %s
                ORDER BY ten_kh
            """, (f"%{kw}%", f"%{kw}%"))
        else:
            cursor.execute("""
                SELECT ma_kh, ten_kh, so_dt, dia_chi
                FROM khach_hang
                ORDER BY ten_kh
            """)

        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())

        for r in rows:
            self.tree.insert("", "end", iid=str(r[0]), values=r)

        self.lbl_count.configure(text=f"{len(rows)} khách hàng")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Thông báo", "Chọn khách hàng!")
            return None
        return int(sel[0])

    # ============================================================
    # ACTIONS
    # ============================================================
    def _add(self):
        CustomerDialog(self, None, self._load)

    def _edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Thông báo", "Chọn khách hàng!")
            return

        vals = self.tree.item(sel[0])["values"]
        CustomerDialog(self, vals, self._load)

    def _delete(self):
        ma = self._selected_id()
        if not ma:
            return

        if not messagebox.askyesno("Xác nhận", "Xóa khách hàng này?"):
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM khach_hang WHERE ma_kh=%s", (ma,))
            conn.commit()
            messagebox.showinfo("Thành công", "Đã xóa khách hàng!")
            self._load()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            conn.close()


# ================================================================
# DIALOG
# ================================================================
class CustomerDialog(ctk.CTkToplevel):
    def __init__(self, parent, data, callback):
        super().__init__(parent)

        self.data = data
        self.callback = callback

        self.title("Thêm khách hàng" if not data else "Sửa khách hàng")
        self.geometry("420x380")
        self.resizable(False, False)
        self.grab_set()

        self._build_ui()

        if data:
            self._fill()

    def _build_ui(self):
        frm = ctk.CTkFrame(self, fg_color="transparent")
        frm.pack(fill="both", expand=True, padx=25, pady=20)

        # Tên
        ctk.CTkLabel(frm, text="Tên khách hàng").pack(anchor="w")
        self.e_name = ctk.CTkEntry(frm, height=36)
        self.e_name.pack(fill="x", pady=6)

        # SĐT
        ctk.CTkLabel(frm, text="Số điện thoại").pack(anchor="w")
        self.e_phone = ctk.CTkEntry(frm, height=36)
        self.e_phone.pack(fill="x", pady=6)

        # Địa chỉ
        ctk.CTkLabel(frm, text="Địa chỉ").pack(anchor="w")
        self.e_addr = ctk.CTkEntry(frm, height=36)
        self.e_addr.pack(fill="x", pady=6)

        # Button
        ctk.CTkButton(
            frm,
            text="Lưu",
            height=42,
            command=self._save
        ).pack(fill="x", pady=15)

    def _fill(self):
        self.e_name.insert(0, self.data[1])
        self.e_phone.insert(0, self.data[2] or "")
        self.e_addr.insert(0, self.data[3] or "")

    def _save(self):
        name = self.e_name.get().strip()

        if not name:
            messagebox.showwarning("Lỗi", "Tên không được trống!")
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            if self.data:
                cursor.execute("""
                    UPDATE khach_hang
                    SET ten_kh=%s, so_dt=%s, dia_chi=%s
                    WHERE ma_kh=%s
                """, (name, self.e_phone.get(), self.e_addr.get(), self.data[0]))
            else:
                cursor.execute("""
                    INSERT INTO khach_hang (ten_kh, so_dt, dia_chi)
                    VALUES (%s,%s,%s)
                """, (name, self.e_phone.get(), self.e_addr.get()))

            conn.commit()

            messagebox.showinfo("Thành công", "Đã lưu!")
            self.callback()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            conn.close()