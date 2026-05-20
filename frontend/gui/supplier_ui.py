import customtkinter as ctk
from tkinter import ttk, messagebox
from frontend.gui.theme import *
from backend.modules import supplier_service as svc
from backend.models.supplier import Supplier


class SupplierFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._only_active = True
        self._build_ui(); self._load()

    def _build_ui(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=SP_LG, pady=(SP_LG,SP_SM))
        page_header(tb,"🏭  Nhà cung cấp",
                    "Quản lý đối tác cung cấp hàng hóa").pack(side="left")
        bf = ctk.CTkFrame(tb, fg_color="transparent")
        bf.pack(side="right")
        make_btn(bf,"Đổi TT",self._toggle,"warning",width=110,icon="🔄").pack(side="right",padx=(4,0))
        make_btn(bf,"Sửa",   self._edit,  "warning",width=100,icon="✏️").pack(side="right",padx=4)
        make_btn(bf,"Thêm",  self._add,   "primary", width=110,icon="➕").pack(side="right")

        sb = make_card(self); sb.pack(fill="x",padx=SP_LG,pady=(0,SP_SM))
        sr = ctk.CTkFrame(sb,fg_color="transparent")
        sr.pack(fill="x",padx=SP_MD,pady=SP_SM)
        self.ent_search = ctk.CTkEntry(sr,height=BTN_MD,
            placeholder_text="🔍  Tìm tên, SĐT, email...",
            font=ctk.CTkFont(size=FS_MD),
            corner_radius=RADIUS_SM, border_color=BORDER)
        self.ent_search.pack(side="left",fill="x",expand=True)
        self.ent_search.bind("<KeyRelease>",lambda _: self._load())
        self.chk_active = ctk.CTkCheckBox(sr,text="Chỉ đang HĐ",
            font=ctk.CTkFont(size=FS_SM),
            command=self._load)
        self.chk_active.pack(side="right",padx=(SP_MD,0))
        self.chk_active.select()
        self.lbl_count = ctk.CTkLabel(sr,text="",
            font=ctk.CTkFont(size=FS_SM),text_color=TEXT_GRAY)
        self.lbl_count.pack(side="right",padx=(SP_MD,0))

        tbl = make_card(self); tbl.pack(fill="both",expand=True,padx=SP_LG,pady=(0,SP_LG))
        style = ttk.Style(); tv = apply_treeview_style(style)
        cols = ("Mã NCC","Tên NCC","Người LH","Số điện thoại","Email","Trạng thái")
        self.tree = ttk.Treeview(tbl,columns=cols,show="headings",style=tv)
        cfg = [("Mã NCC",70,"center"),("Tên NCC",220,"center"),
               ("Người LH",140,"center"),("Số điện thoại",130,"center"),
               ("Email",180,"center"),("Trạng thái",100,"center")]
        for col,w,a in cfg:
            self.tree.heading(col,text=col,anchor="center")
            self.tree.column(col,width=w,anchor=a,minwidth=w,stretch=False)
        self.tree.tag_configure("odd",  background="#F7FAFF")
        self.tree.tag_configure("even", background="#FFFFFF")
        self.tree.tag_configure("inactive",foreground="#9E9E9E",background="#FAFAFA")
        sy = ttk.Scrollbar(tbl,orient="vertical",
                            command=self.tree.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=sy.set)
        self.tree.pack(side="left",fill="both",expand=True,padx=(SP_SM,0),pady=SP_SM)
        sy.pack(side="right",fill="y",pady=SP_SM,padx=(0,4))
        self.tree.bind("<Double-1>",lambda _: self._edit())

    def _load(self):
        kw = self.ent_search.get().strip()
        only = self.chk_active.get() == 1
        items = svc.get_all(kw, only)
        for r in self.tree.get_children(): self.tree.delete(r)
        for i,s in enumerate(items):
            tag = "inactive" if not s.trang_thai \
                  else ("odd" if i%2 else "even")
            tt = "Hoạt động" if s.trang_thai else "Ngừng HĐ"
            self.tree.insert("","end",iid=str(s.ma_ncc),
                values=(s.ma_ncc,s.ten_ncc,s.nguoi_lh or "—",
                        s.so_dt or "—",s.email or "—",tt),
                tags=(tag,))
        self.lbl_count.configure(text=f"{len(items)} NCC")

    def _sel(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn","Chọn nhà cung cấp!"); return None
        return int(sel[0])

    def _add(self): SupplierDialog(self,None,self._load)
    def _edit(self):
        mid = self._sel()
        if mid:
            s = svc.get_by_id(mid)
            if s: SupplierDialog(self,s,self._load)
    def _toggle(self):
        mid = self._sel()
        if not mid: return
        s = svc.get_by_id(mid)
        if not s: return
        new = 0 if s.trang_thai else 1
        act = "ngừng" if new==0 else "kích hoạt"
        if messagebox.askyesno("Xác nhận",f"{act.capitalize()} NCC «{s.ten_ncc}»?"):
            ok,msg = svc.toggle_status(mid)
            (messagebox.showinfo if ok else messagebox.showerror)("Kết quả",msg)
            if ok: self._load()


class SupplierDialog(ctk.CTkToplevel):
    def __init__(self, parent, supplier, callback):
        super().__init__(parent)
        self.s = supplier; self.callback = callback
        self.title("Thêm NCC" if not supplier else "Sửa NCC")
        self.geometry("460x500"); self.resizable(False,False)
        self.configure(fg_color=CARD); self.grab_set()
        self._build()
        if supplier: self._fill()

    def _build(self):
        hdr = ctk.CTkFrame(self,fg_color=PRIMARY,corner_radius=0,height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr,
            text="➕  Thêm nhà cung cấp" if not self.s else "✏️  Sửa nhà cung cấp",
            font=ctk.CTkFont(size=FS_LG,weight="bold"),
            text_color="white").pack(expand=True)
        body = ctk.CTkFrame(self,fg_color=CARD)
        body.pack(fill="both",expand=True,padx=SP_XL,pady=SP_MD)
        def f(label,attr,placeholder=""):
            ctk.CTkLabel(body,text=label,anchor="w",
                font=ctk.CTkFont(size=FS_SM,weight="bold"),
                text_color=TEXT_SECOND).pack(fill="x",pady=(8,2))
            e = ctk.CTkEntry(body,height=BTN_MD,
                font=ctk.CTkFont(size=FS_MD),
                placeholder_text=placeholder,
                fg_color=CARD,border_color=BORDER,
                corner_radius=RADIUS_SM)
            e.pack(fill="x"); setattr(self,attr,e)
        f("Tên nhà cung cấp *","e_name","Công ty TNHH ABC")
        f("Người liên hệ","e_nguoilh","Nguyễn Văn A")
        f("Số điện thoại","e_sdt","028 xxxx xxxx")
        f("Email","e_email","contact@abc.com")
        f("Địa chỉ","e_addr","Địa chỉ công ty")
        ctk.CTkFrame(body,fg_color=BORDER,height=1).pack(fill="x",pady=(SP_MD,SP_SM))
        make_btn(body,"Lưu",self._save,"primary",height=BTN_LG,icon="💾").pack(fill="x")

    def _fill(self):
        self.e_name.insert(0,self.s.ten_ncc)
        self.e_nguoilh.insert(0,self.s.nguoi_lh or "")
        self.e_sdt.insert(0,self.s.so_dt or "")
        self.e_email.insert(0,self.s.email or "")
        self.e_addr.insert(0,self.s.dia_chi or "")

    def _save(self):
        s = Supplier(
            ma_ncc=self.s.ma_ncc if self.s else None,
            ten_ncc=self.e_name.get().strip(),
            nguoi_lh=self.e_nguoilh.get().strip(),
            so_dt=self.e_sdt.get().strip(),
            email=self.e_email.get().strip(),
            dia_chi=self.e_addr.get().strip())
        ok,msg = svc.update(s) if self.s else svc.add(s)
        (messagebox.showinfo if ok else messagebox.showerror)("Kết quả",msg)
        if ok: self.callback(); self.destroy()
