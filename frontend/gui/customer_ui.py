import customtkinter as ctk
from tkinter import ttk, messagebox
from frontend.gui.theme import *
from backend.modules import customer_service as svc
from backend.models.customer import Customer
from backend.database.connection import get_connection


def _hang_info(ma_kh):
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute(
            "SELECT hang_khach_hang, diem_tich_luy, tong_chi_tieu "
            "FROM khach_hang WHERE ma_kh=%s", (ma_kh,))
        row = cur.fetchone(); conn.close()
        return (row[0] or "Thường",
                int(row[1] or 0),
                float(row[2] or 0)) if row else ("Thường",0,0)
    except Exception:
        return "Thường", 0, 0


HANG_COLOR = {
    "Bạch Kim": (PURPLE, "#F3E8FF"),
    "Vàng":     ("#B8860B", "#FFFDE7"),
    "Bạc":      ("#607D8B", "#F5F5F5"),
    "Thường":   (TEXT_GRAY, "transparent"),
}


class CustomerFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build_ui(); self._load()

    def _build_ui(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=SP_LG, pady=(SP_LG, SP_SM))
        page_header(tb, "👥  Quản lý Khách hàng",
                    "CRUD khách hàng, điểm tích lũy và hạng thành viên"
                    ).pack(side="left")
        bf = ctk.CTkFrame(tb, fg_color="transparent")
        bf.pack(side="right")
        make_btn(bf,"Xóa",  self._delete,"danger", width=100,icon="🗑").pack(side="right",padx=(4,0))
        make_btn(bf,"Sửa",  self._edit,  "warning",width=100,icon="✏️").pack(side="right",padx=4)
        make_btn(bf,"Thêm", self._add,   "primary", width=110,icon="➕").pack(side="right")

        sb = make_card(self)
        sb.pack(fill="x", padx=SP_LG, pady=(0,SP_SM))
        sr = ctk.CTkFrame(sb, fg_color="transparent")
        sr.pack(fill="x", padx=SP_MD, pady=SP_SM)
        self.ent_search = ctk.CTkEntry(sr, height=BTN_MD,
            placeholder_text="🔍  Tìm tên, SĐT, email...",
            font=ctk.CTkFont(size=FS_MD),
            corner_radius=RADIUS_SM, border_color=BORDER)
        self.ent_search.pack(side="left", fill="x", expand=True)
        self.ent_search.bind("<KeyRelease>", lambda _: self._load())
        self.lbl_count = ctk.CTkLabel(sr, text="",
            font=ctk.CTkFont(size=FS_SM), text_color=TEXT_GRAY)
        self.lbl_count.pack(side="right", padx=(SP_MD,0))

        tbl = make_card(self)
        tbl.pack(fill="both", expand=True, padx=SP_LG, pady=(0,SP_LG))
        style = ttk.Style()
        tv = apply_treeview_style(style)
        cols = ("Mã KH","Họ và tên","Số điện thoại","Địa chỉ","Hạng KH","Điểm","Chi tiêu")
        self.tree = ttk.Treeview(tbl, columns=cols,
                                  show="headings", style=tv)
        cfg = [("Mã KH",70,"center"),("Họ và tên",200,"center"),
               ("Số điện thoại",120,"center"),("Địa chỉ",220,"center"),
               ("Hạng KH",90,"center"),("Điểm",80,"center"),
               ("Chi tiêu",120,"center")]
        for col,w,a in cfg:
            self.tree.heading(col,text=col,anchor="center")
            self.tree.column(col,width=w,anchor=a,minwidth=w,stretch=False)
        for hang,(color,bg) in HANG_COLOR.items():
            self.tree.tag_configure(hang, foreground=color,
                                    background=bg if bg != "transparent" else "#FFFFFF")
        self.tree.tag_configure("odd",  background="#F7FAFF")
        self.tree.tag_configure("even", background="#FFFFFF")
        sy = ttk.Scrollbar(tbl, orient="vertical",
                            command=self.tree.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=sy.set)
        self.tree.pack(side="left", fill="both", expand=True,
                       padx=(SP_SM,0), pady=SP_SM)
        sy.pack(side="right", fill="y", pady=SP_SM, padx=(0,4))
        self.tree.bind("<Double-1>", lambda _: self._edit())

    def _load(self):
        kw = self.ent_search.get().strip()
        items = svc.get_all(kw)
        for r in self.tree.get_children(): self.tree.delete(r)
        for i, c in enumerate(items):
            hang, diem, chi = _hang_info(c.ma_kh)
            tag = hang if hang in HANG_COLOR and hang != "Thường" \
                  else ("odd" if i%2 else "even")
            self.tree.insert("","end",iid=str(c.ma_kh),
                values=(c.ma_kh, c.ten_kh, c.so_dt or "—",
                        c.dia_chi or "—", hang,
                        f"{diem:,}", f"{chi:,.0f}đ"),
                tags=(tag,))
        self.lbl_count.configure(text=f"{len(items)} khách hàng")

    def _sel_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn","Vui lòng chọn khách hàng!")
            return None
        return int(sel[0])

    def _add(self): CustomerDialog(self, None, self._load)
    def _edit(self):
        mid = self._sel_id()
        if mid:
            c = svc.get_by_id(mid)
            if c: CustomerDialog(self, c, self._load)
    def _delete(self):
        mid = self._sel_id()
        if not mid: return
        name = self.tree.item(str(mid))["values"][1]
        if messagebox.askyesno("Xác nhận", f"Xóa khách hàng «{name}»?"):
            ok,msg = svc.delete(mid)
            (messagebox.showinfo if ok else messagebox.showerror)("Kết quả",msg)
            if ok: self._load()


class CustomerDialog(ctk.CTkToplevel):
    def __init__(self, parent, customer, callback):
        super().__init__(parent)
        self.customer = customer; self.callback = callback
        self.title("Thêm khách hàng" if not customer else "Sửa khách hàng")
        self.geometry("460x440"); self.resizable(False,False)
        self.configure(fg_color=CARD); self.grab_set()
        self._build()
        if customer: self._fill()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=PRIMARY, corner_radius=0, height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr,
            text="➕  Thêm khách hàng" if not self.customer else "✏️  Sửa khách hàng",
            font=ctk.CTkFont(size=FS_LG, weight="bold"),
            text_color="white").pack(expand=True)
        body = ctk.CTkFrame(self, fg_color=CARD)
        body.pack(fill="both", expand=True, padx=SP_XL, pady=SP_MD)
        def f(label, attr, placeholder=""):
            ctk.CTkLabel(body, text=label, anchor="w",
                font=ctk.CTkFont(size=FS_SM, weight="bold"),
                text_color=TEXT_SECOND).pack(fill="x", pady=(8,2))
            e = ctk.CTkEntry(body, height=BTN_MD,
                font=ctk.CTkFont(size=FS_MD),
                placeholder_text=placeholder,
                fg_color=CARD, border_color=BORDER,
                corner_radius=RADIUS_SM)
            e.pack(fill="x"); setattr(self, attr, e)
        f("Họ và tên *","e_name","Nguyễn Văn A")
        f("Số điện thoại","e_phone","0901 234 567")
        f("Địa chỉ","e_addr","Số nhà, đường, quận...")
        f("Email","e_email","email@gmail.com")
        ctk.CTkFrame(body,fg_color=BORDER,height=1).pack(fill="x",pady=(SP_MD,SP_SM))
        make_btn(body,"Lưu thông tin",self._save,"primary",
                 height=BTN_LG,icon="💾").pack(fill="x")

    def _fill(self):
        c = self.customer
        self.e_name.insert(0, c.ten_kh)
        self.e_phone.insert(0, c.so_dt or "")
        self.e_addr.insert(0, c.dia_chi or "")
        self.e_email.insert(0, c.email or "")

    def _save(self):
        c = Customer(
            ma_kh=self.customer.ma_kh if self.customer else None,
            ten_kh=self.e_name.get().strip(),
            so_dt=self.e_phone.get().strip(),
            dia_chi=self.e_addr.get().strip(),
            email=self.e_email.get().strip())
        ok,msg = svc.update(c) if self.customer else svc.add(c)
        (messagebox.showinfo if ok else messagebox.showerror)("Kết quả",msg)
        if ok: self.callback(); self.destroy()
