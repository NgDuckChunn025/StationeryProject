import customtkinter as ctk
from tkinter import ttk, messagebox
from frontend.gui.theme import *
from backend.modules import staff_service as svc


class StaffFrame(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.current_user = user
        self._build_ui(); self._load()

    def _build_ui(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=SP_LG, pady=(SP_LG, SP_SM))
        page_header(tb, "👤  Quản lý Nhân viên",
                    "Thêm, sửa, phân quyền và khóa tài khoản").pack(side="left")
        bf = ctk.CTkFrame(tb, fg_color="transparent"); bf.pack(side="right")
        make_btn(bf,"Khóa/Mở",self._toggle,"warning",width=110,icon="🔒").pack(side="right",padx=(4,0))
        make_btn(bf,"Sửa",    self._edit,  "primary", width=100,icon="✏️").pack(side="right",padx=4)
        make_btn(bf,"Thêm",   self._add,   "success", width=110,icon="➕").pack(side="right")

        tbl = make_card(self); tbl.pack(fill="both",expand=True,padx=SP_LG,pady=(SP_SM,SP_LG))
        style=ttk.Style(); tv=apply_treeview_style(style)
        cols=("Mã NV","Họ và tên","Tài khoản","Vai trò","Số điện thoại","Trạng thái")
        self.tree=ttk.Treeview(tbl,columns=cols,show="headings",style=tv,selectmode="browse")
        for col,w,a in [("Mã NV",65,"center"),("Họ và tên",210,"center"),
                        ("Tài khoản",130,"center"),("Vai trò",100,"center"),
                        ("Số điện thoại",130,"center"),("Trạng thái",100,"center")]:
            self.tree.heading(col,text=col,anchor="center")
            self.tree.column(col,width=w,anchor=a,minwidth=w,stretch=False)
        self.tree.tag_configure("odd",   background="#F7FAFF")
        self.tree.tag_configure("even",  background="#FFFFFF")
        self.tree.tag_configure("admin", background=PRIMARY_LIGHT,foreground=PRIMARY_DARK)
        self.tree.tag_configure("locked",foreground="#9E9E9E",background="#FAFAFA")
        sy=ttk.Scrollbar(tbl,orient="vertical",command=self.tree.yview,style="VPP.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=sy.set)
        self.tree.pack(side="left",fill="both",expand=True,padx=(SP_SM,0),pady=SP_SM)
        sy.pack(side="right",fill="y",pady=SP_SM,padx=(0,4))
        self.tree.bind("<Double-1>",lambda _: self._edit())

    def _load(self):
        rows=svc.get_all()
        for r in self.tree.get_children(): self.tree.delete(r)
        for i,row in enumerate(rows):
            ma_nv,ten,tk,role,so_dt,trang_thai=row
            if not trang_thai:   tag="locked"
            elif role=="admin":  tag="admin"
            else:                tag="odd" if i%2 else "even"
            role_str="Quản trị viên" if role=="admin" else "Nhân viên"
            tt_str  ="Hoạt động" if trang_thai else "Đã khóa"
            self.tree.insert("","end",iid=str(ma_nv),
                values=(ma_nv,ten,tk,role_str,so_dt or "—",tt_str),tags=(tag,))

    def _sel(self):
        sel=self.tree.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn","Vui lòng chọn nhân viên!"); return None
        return int(sel[0])

    def _add(self):    StaffDialog(self,None,self.current_user,self._load)
    def _edit(self):
        mid=self._sel()
        if mid: StaffDialog(self,mid,self.current_user,self._load)

    def _toggle(self):
        mid=self._sel()
        if not mid: return
        if mid==self.current_user["ma_nv"]:
            messagebox.showwarning("Không thể","Bạn không thể khóa chính mình!"); return
        ok,msg=svc.toggle_status(mid)
        (messagebox.showinfo if ok else messagebox.showerror)("Kết quả",msg)
        if ok: self._load()


class StaffDialog(ctk.CTkToplevel):
    def __init__(self, parent, ma_nv, current_user, callback):
        super().__init__(parent)
        self.ma_nv=ma_nv; self.current_user=current_user; self.callback=callback
        self.title("Thêm nhân viên" if not ma_nv else "Sửa nhân viên")
        self.geometry("460x500"); self.resizable(False,False)
        self.configure(fg_color=CARD); self.grab_set()
        self._build()
        if ma_nv: self._fill()

    def _build(self):
        hdr=ctk.CTkFrame(self,fg_color=PRIMARY,corner_radius=0,height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr,
            text="➕  Thêm nhân viên mới" if not self.ma_nv else "✏️  Sửa nhân viên",
            font=ctk.CTkFont(size=FS_LG,weight="bold"),text_color="white").pack(expand=True)
        body=ctk.CTkFrame(self,fg_color=CARD)
        body.pack(fill="both",expand=True,padx=SP_XL,pady=SP_MD)

        def f(label,attr,placeholder="",show=""):
            ctk.CTkLabel(body,text=label,anchor="w",
                font=ctk.CTkFont(size=FS_SM,weight="bold"),text_color=TEXT_SECOND).pack(fill="x",pady=(8,2))
            kw=dict(height=BTN_MD,font=ctk.CTkFont(size=FS_MD),placeholder_text=placeholder,
                fg_color=CARD,border_color=BORDER,corner_radius=RADIUS_SM)
            if show: kw["show"]=show
            e=ctk.CTkEntry(body,**kw); e.pack(fill="x"); setattr(self,attr,e)

        f("Họ và tên *",  "e_name", "Nguyễn Văn A")
        f("Tài khoản *",  "e_user", "vd: nv01")
        f("Số điện thoại","e_phone","0901 234 567")
        hint_pw="Để trống = giữ mật khẩu cũ" if self.ma_nv else "Tối thiểu 6 ký tự"
        f("Mật khẩu","e_pass",hint_pw,show="•")

        ctk.CTkLabel(body,text="Vai trò",anchor="w",
            font=ctk.CTkFont(size=FS_SM,weight="bold"),text_color=TEXT_SECOND).pack(fill="x",pady=(8,2))
        self.cmb_role=ctk.CTkComboBox(body,values=["nhanvien","admin"],height=BTN_MD,
            font=ctk.CTkFont(size=FS_MD),fg_color=CARD,border_color=BORDER,corner_radius=RADIUS_SM)
        self.cmb_role.pack(fill="x"); self.cmb_role.set("nhanvien")

        ctk.CTkFrame(body,fg_color=BORDER,height=1).pack(fill="x",pady=(SP_MD,SP_SM))
        make_btn(body,"Lưu nhân viên",self._save,"primary",height=BTN_LG,icon="💾").pack(fill="x")

    def _fill(self):
        from backend.database.connection import get_connection
        conn=get_connection(); cur=conn.cursor()
        cur.execute("SELECT ten_nv,tai_khoan,vai_tro,COALESCE(so_dt,'') FROM nhan_vien WHERE ma_nv=%s",(self.ma_nv,))
        row=cur.fetchone(); conn.close()
        if not row: return
        self.e_name.insert(0,row[0])
        self.e_user.insert(0,row[1]); self.e_user.configure(state="disabled")
        self.cmb_role.set(row[2] or "nhanvien")
        self.e_phone.insert(0,row[3])

    def _save(self):
        name =self.e_name.get().strip()
        uname=self.e_user.get().strip()
        pw   =self.e_pass.get().strip()
        role =self.cmb_role.get()
        phone=self.e_phone.get().strip()
        if not name or not uname:
            messagebox.showwarning("Thiếu thông tin","Vui lòng nhập họ tên và tài khoản!"); return
        if not self.ma_nv and not pw:
            messagebox.showwarning("Thiếu mật khẩu","Phải nhập mật khẩu khi tạo mới!"); return
        if self.ma_nv:
            ok,msg=svc.update(self.ma_nv,name,role,phone,pw or None)
        else:
            ok,msg=svc.add(name,uname,pw,role,phone)
        (messagebox.showinfo if ok else messagebox.showerror)("Kết quả",msg)
        if ok: self.callback(); self.destroy()
