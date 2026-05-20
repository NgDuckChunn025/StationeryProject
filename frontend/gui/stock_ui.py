import customtkinter as ctk
from tkinter import ttk, messagebox
from frontend.gui.theme import *
from backend.modules import product_service as psvc
from backend.modules import stock_service as ssvc
from backend.models.stock_entry import StockEntry


class StockFrame(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self.entry = StockEntry(user["ma_nv"], user["ten_nv"])
        self._ncc_map = {}
        self._build_ui()
        self._load_products()
        self._reload_ncc()
        self._load_history()

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=SP_LG, pady=(SP_LG, SP_SM))
        page_header(hdr,"📥  Nhập kho","Tạo phiếu nhập và cập nhật tồn kho").pack(side="left")

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=SP_MD, pady=(0,SP_MD))
        self._build_left(main)
        self._build_right(main)

    def _build_left(self, parent):
        frm = make_card(parent)
        frm.pack(side="left", fill="both", expand=True, padx=(0,SP_SM))

        tabs = ctk.CTkTabview(frm)
        tabs.pack(fill="both", expand=True, padx=4, pady=4)
        t1 = tabs.add("📦  Sản phẩm")
        t2 = tabs.add("📋  Lịch sử nhập")

        # Tab SP
        self.ent_search = ctk.CTkEntry(t1, height=BTN_MD,
            placeholder_text="🔍  Tìm tên / mã sản phẩm...",
            font=ctk.CTkFont(size=FS_MD), corner_radius=RADIUS_SM, border_color=BORDER)
        self.ent_search.pack(fill="x", padx=SP_SM, pady=(SP_SM,4))
        self.ent_search.bind("<KeyRelease>", lambda _: self._load_products())

        style = ttk.Style(); tv = apply_treeview_style(style)
        cols = ("Mã","Tên sản phẩm","Giá nhập","Tồn kho")
        self.tree_sp = ttk.Treeview(t1, columns=cols, show="headings", style=tv, height=14)
        for col,w,a in [("Mã",75,"center"),("Tên sản phẩm",260,"center"),("Giá nhập",110,"center"),("Tồn kho",80,"center")]:
            self.tree_sp.heading(col,text=col,anchor="center")
            self.tree_sp.column(col,width=w,anchor=a,minwidth=w,stretch=False)
        self.tree_sp.tag_configure("odd", background="#F7FAFF")
        self.tree_sp.tag_configure("even",background="#FFFFFF")
        sy1 = ttk.Scrollbar(t1,orient="vertical",command=self.tree_sp.yview,style="VPP.Vertical.TScrollbar")
        self.tree_sp.configure(yscrollcommand=sy1.set)
        self.tree_sp.pack(side="left",fill="both",expand=True,padx=(SP_SM,0),pady=(0,4))
        sy1.pack(side="right",fill="y",pady=(0,4),padx=(0,4))
        self.tree_sp.bind("<Double-1>",self._add_item)
        ctk.CTkLabel(t1,text="Double-click để thêm vào phiếu",
            font=ctk.CTkFont(size=FS_XS),text_color=TEXT_GRAY).pack(pady=(0,4))

        # Tab lịch sử
        cols2 = ("Mã phiếu","Nhà CC","Nhân viên","Ngày nhập","Tổng tiền")
        self.tree_his = ttk.Treeview(t2, columns=cols2, show="headings", style=tv, height=16)
        for col in cols2:
            self.tree_his.heading(col,text=col,anchor="center")
            self.tree_his.column(col,width=120,anchor="center",minwidth=80,stretch=False)
        self.tree_his.tag_configure("odd", background="#F7FAFF")
        self.tree_his.tag_configure("even",background="#FFFFFF")
        sy2 = ttk.Scrollbar(t2,orient="vertical",command=self.tree_his.yview,style="VPP.Vertical.TScrollbar")
        self.tree_his.configure(yscrollcommand=sy2.set)
        self.tree_his.pack(side="left",fill="both",expand=True,padx=(SP_SM,0),pady=SP_SM)
        sy2.pack(side="right",fill="y",pady=SP_SM,padx=(0,4))

    def _build_right(self, parent):
        frm = make_card(parent); frm.configure(width=400)
        frm.pack(side="right",fill="y"); frm.pack_propagate(False)

        ctk.CTkLabel(frm,text="📝  Phiếu nhập kho",
            font=ctk.CTkFont(size=FS_LG,weight="bold"),text_color=TEXT_PRIMARY).pack(pady=(SP_MD,SP_SM))

        # NCC section
        ncc_f = ctk.CTkFrame(frm,fg_color=PRIMARY_LIGHT,corner_radius=RADIUS_SM)
        ncc_f.pack(fill="x",padx=SP_MD,pady=(0,SP_SM))
        ncc_h = ctk.CTkFrame(ncc_f,fg_color="transparent"); ncc_h.pack(fill="x",padx=SP_SM,pady=(SP_SM,2))
        ctk.CTkLabel(ncc_h,text="Nhà cung cấp:",font=ctk.CTkFont(size=FS_SM,weight="bold"),text_color=TEXT_SECOND).pack(side="left")
        ncc_r = ctk.CTkFrame(ncc_f,fg_color="transparent"); ncc_r.pack(fill="x",padx=SP_SM,pady=(0,SP_SM))
        self.cmb_ncc = ctk.CTkComboBox(ncc_r,values=["(Chưa có NCC)"],height=BTN_SM,
            font=ctk.CTkFont(size=FS_MD),fg_color=CARD,border_color=BORDER,corner_radius=RADIUS_SM)
        self.cmb_ncc.pack(side="left",fill="x",expand=True)
        make_btn(ncc_r,"",self._reload_ncc,"ghost",width=30,height=BTN_SM,icon="🔄").pack(side="right",padx=(4,0))

        # Items
        style=ttk.Style(); tv=apply_treeview_style(style)
        cols_e=("Tên sản phẩm","Đơn giá","SL","Thành tiền")
        self.tree_entry = ttk.Treeview(frm,columns=cols_e,show="headings",style=tv,height=10)
        for col,w,a in [("Tên sản phẩm",145,"center"),("Đơn giá",82,"center"),("SL",42,"center"),("Thành tiền",95,"center")]:
            self.tree_entry.heading(col,text=col,anchor="center")
            self.tree_entry.column(col,width=w,anchor=a,minwidth=w,stretch=False)
        self.tree_entry.pack(fill="x",padx=SP_MD,pady=(SP_SM,0))
        make_btn(frm,"Xóa dòng đã chọn",self._remove_item,"danger",height=BTN_SM,icon="🗑").pack(fill="x",padx=SP_MD,pady=4)

        ctk.CTkLabel(frm,text="Ghi chú:",anchor="w",font=ctk.CTkFont(size=FS_SM,weight="bold"),text_color=TEXT_SECOND).pack(fill="x",padx=SP_MD)
        self.ent_note = ctk.CTkEntry(frm,height=BTN_SM,placeholder_text="Ghi chú phiếu nhập...",
            font=ctk.CTkFont(size=FS_MD),fg_color=CARD,border_color=BORDER,corner_radius=RADIUS_SM)
        self.ent_note.pack(fill="x",padx=SP_MD,pady=(2,SP_SM))

        total_f = ctk.CTkFrame(frm,fg_color=SUCCESS_LIGHT,corner_radius=RADIUS_SM)
        total_f.pack(fill="x",padx=SP_MD,pady=(0,SP_SM))
        self.lbl_total = ctk.CTkLabel(total_f,text="TỔNG:  0đ",
            font=ctk.CTkFont(size=FS_LG,weight="bold"),text_color=SUCCESS)
        self.lbl_total.pack(pady=SP_MD)

        make_btn(frm,"LƯU PHIẾU NHẬP",self._save,"success",height=BTN_LG,icon="💾").pack(fill="x",padx=SP_MD,pady=4)
        make_btn(frm,"Phiếu mới",self._new,"ghost",height=BTN_SM,icon="🔄").pack(fill="x",padx=SP_MD)

    def _load_products(self):
        kw = self.ent_search.get().strip()
        items = psvc.search(kw) if kw else psvc.get_all()
        for r in self.tree_sp.get_children(): self.tree_sp.delete(r)
        for i,p in enumerate(items):
            self.tree_sp.insert("","end",iid=str(p.ma_sp),
                values=(p.ma_code,p.ten_sp,p.fmt_gia_nhap(),p.ton_kho),
                tags=("odd" if i%2 else "even",))

    def _reload_ncc(self):
        try:
            suppliers = ssvc.get_suppliers()
            self._ncc_map = {s[1]:s[0] for s in suppliers}
        except Exception: self._ncc_map = {}
        vals = list(self._ncc_map.keys()) if self._ncc_map else ["(Chưa có NCC)"]
        self.cmb_ncc.configure(values=vals)
        if vals: self.cmb_ncc.set(vals[0])

    def _load_history(self):
        try: rows = ssvc.get_entries()
        except Exception: rows = []
        for r in self.tree_his.get_children(): self.tree_his.delete(r)
        for i,row in enumerate(rows):
            ma,ncc,nv,ngay,tong,_ = row
            self.tree_his.insert("","end",
                values=(f"#{ma:04d}",ncc,nv,str(ngay)[:10],f"{float(tong or 0):,.0f}đ"),
                tags=("odd" if i%2 else "even",))

    def _add_item(self,_=None):
        sel = self.tree_sp.selection()
        if not sel: return
        v=self.tree_sp.item(sel[0])["values"]
        ma_sp=int(sel[0]); ten_sp=str(v[1])
        gia=float(str(v[2]).replace("đ","").replace(",",""))
        dlg=ctk.CTkInputDialog(text=f"Số lượng nhập ({ten_sp}):",title="Nhập số lượng")
        qty=dlg.get_input()
        if not qty: return
        try:
            qty=int(qty)
            if qty<=0: raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi","Số lượng phải là số nguyên dương!"); return
        self.entry.add_item(ma_sp,ten_sp,gia,qty); self._refresh()

    def _remove_item(self):
        sel=self.tree_entry.selection()
        if sel: self.entry.remove_item(int(sel[0])); self._refresh()

    def _refresh(self):
        for r in self.tree_entry.get_children(): self.tree_entry.delete(r)
        for item in self.entry.items:
            self.tree_entry.insert("","end",iid=str(item.ma_sp),values=item.to_table_row())
        self.lbl_total.configure(text=f"TỔNG:  {self.entry.tong_tien:,.0f}đ")

    def _save(self):
        if not self.entry.items:
            messagebox.showwarning("Phiếu trống","Vui lòng thêm sản phẩm!"); return
        self.entry.ma_ncc=self._ncc_map.get(self.cmb_ncc.get())
        self.entry.ghi_chu=self.ent_note.get().strip()
        if not messagebox.askyesno("Xác nhận",f"Lưu phiếu {self.entry.so_dong} mặt hàng, tổng {self.entry.tong_tien:,.0f}đ?"): return
        ok,result = ssvc.create_entry(self.entry)
        if ok:
            messagebox.showinfo("Thành công",f"Đã lưu phiếu #{result:04d}!")
            self._new(); self._load_history()
        else: messagebox.showerror("Lỗi",str(result))

    def _new(self):
        self.entry=StockEntry(self.user["ma_nv"],self.user["ten_nv"])
        self._refresh(); self.ent_note.delete(0,"end")

    def _add_ncc(self):
        dlg=ctk.CTkInputDialog(text="Tên nhà cung cấp mới:",title="Thêm NCC")
        name=dlg.get_input()
        if not name or not name.strip(): return
        ok,msg=ssvc.add_supplier(name.strip())
        (messagebox.showinfo if ok else messagebox.showerror)("Kết quả",msg)
        if ok: self._reload_ncc()
