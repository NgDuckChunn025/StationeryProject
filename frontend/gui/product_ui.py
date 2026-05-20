import os
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from frontend.gui.theme import *
from backend.modules import product_service as svc
from backend.models.product import Product
from PIL import Image

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "product_images")
os.makedirs(IMG_DIR, exist_ok=True)


class ProductFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build_ui(); self._load()

    def _build_ui(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=SP_LG, pady=(SP_LG, SP_SM))
        page_header(tb,"📦  Quản lý Sản phẩm",
                    "Thêm, sửa, xóa sản phẩm — hỗ trợ ảnh đại diện").pack(side="left")
        bf = ctk.CTkFrame(tb, fg_color="transparent"); bf.pack(side="right")
        make_btn(bf,"Xóa", self._delete,"danger", width=100,icon="🗑").pack(side="right",padx=(4,0))
        make_btn(bf,"Sửa", self._edit,  "warning",width=100,icon="✏️").pack(side="right",padx=4)
        make_btn(bf,"Thêm",self._add,   "primary", width=110,icon="➕").pack(side="right")

        sb = make_card(self); sb.pack(fill="x",padx=SP_LG,pady=(0,SP_SM))
        sr = ctk.CTkFrame(sb,fg_color="transparent"); sr.pack(fill="x",padx=SP_MD,pady=SP_SM)
        self.ent_search = ctk.CTkEntry(sr,height=BTN_MD,
            placeholder_text="🔍  Tìm mã hoặc tên sản phẩm...",
            font=ctk.CTkFont(size=FS_MD),corner_radius=RADIUS_SM,border_color=BORDER)
        self.ent_search.pack(side="left",fill="x",expand=True)
        self.ent_search.bind("<KeyRelease>",lambda _: self._load())
        self.lbl_count = ctk.CTkLabel(sr,text="",font=ctk.CTkFont(size=FS_SM),text_color=TEXT_GRAY)
        self.lbl_count.pack(side="left",padx=SP_MD)
        self.lbl_warn = ctk.CTkLabel(sr,text="",font=ctk.CTkFont(size=FS_SM,weight="bold"),text_color=DANGER)
        self.lbl_warn.pack(side="right")

        tbl_wrap = ctk.CTkFrame(self, fg_color="transparent")
        tbl_wrap.pack(fill="both", expand=True, padx=SP_LG, pady=(0, SP_LG))

        tbl = make_card(tbl_wrap)
        tbl.pack(side="left", fill="both", expand=True)

        # ===== PREVIEW PANEL =====
        self.preview = make_card(tbl_wrap, width=300)
        self.preview.pack(side="right", fill="y", padx=(SP_SM, 0))
        self.preview.pack_propagate(False)

        ctk.CTkLabel(
            self.preview,
            text="📦 Chi tiết sản phẩm",
            font=ctk.CTkFont(size=FS_LG, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=SP_MD, pady=(SP_MD, SP_SM))

        divider(self.preview).pack(fill="x", padx=SP_MD)

        self.preview_img = ctk.CTkLabel(
            self.preview,
            text="📷\nChưa có ảnh",
            width=180,
            height=180,
            fg_color=BG,
            corner_radius=RADIUS_MD,
            font=ctk.CTkFont(size=FS_SM),
            text_color=TEXT_GRAY
        )
        self.preview_img.pack(pady=SP_MD)

        self.preview_name = ctk.CTkLabel(
            self.preview,
            text="Chưa chọn sản phẩm",
            font=ctk.CTkFont(size=FS_LG, weight="bold"),
            text_color=TEXT_PRIMARY,
            wraplength=240,
            justify="center"
        )
        self.preview_name.pack(padx=SP_SM)

        self.preview_info = ctk.CTkLabel(
            self.preview,
            text="",
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=FS_SM),
            text_color=TEXT_SECOND
        )
        self.preview_info.pack(fill="x", padx=SP_MD, pady=SP_MD)

        style = ttk.Style()
        tv = apply_treeview_style(style)
        cols = (
            "Mã SP",
            "Tên sản phẩm",
            "Loại",
            "ĐVT",
            "Giá bán",
            "Tồn kho",
            "Trạng thái"
        )
        self.tree = ttk.Treeview(tbl,columns=cols,show="headings",style=tv,selectmode="browse")
        for col, w, a, s in [
            ("Mã SP", 90, "center", False),
            ("Tên sản phẩm", 260, "center", True),
            ("Loại", 120, "center", False),
            ("ĐVT", 70, "center", False),
            ("Giá bán", 120, "center", False),
            ("Tồn kho", 80, "center", False),
            ("Trạng thái", 120, "center", False)
        ]:
            self.tree.heading(col,text=col,anchor="center")
            self.tree.column(col,width=w,anchor=a,minwidth=w,stretch=s)
        self.tree.tag_configure("odd", background="#F7FAFF")
        self.tree.tag_configure("even",background="#FFFFFF")
        self.tree.tag_configure("low", foreground=DANGER,background=DANGER_LIGHT)
        sy = ttk.Scrollbar(tbl,orient="vertical",command=self.tree.yview,style="VPP.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=sy.set)
        self.tree.pack(side="left",fill="both",expand=True,padx=(SP_SM,0),pady=SP_SM)
        sy.pack(side="right",fill="y",pady=SP_SM,padx=(0,4))
        self.tree.bind("<Double-1>",lambda _: self._edit())
        self.tree.bind("<<TreeviewSelect>>", self._show_preview)

    def _load(self):
        kw = self.ent_search.get().strip()
        items = svc.search(kw) if kw else svc.get_all()
        for r in self.tree.get_children(): self.tree.delete(r)
        low = 0
        for i,p in enumerate(items):
            tag = "low" if p.sap_het else ("odd" if i%2 else "even")
            if p.sap_het: low += 1
            self.tree.insert("","end",iid=str(p.ma_sp),
                values=(p.ma_code,p.ten_sp,p.ten_loai or "—",p.don_vi or "—",
                        p.fmt_gia_nhap(),p.fmt_gia_ban(),p.ton_kho),tags=(tag,))
        self.lbl_count.configure(text=f"{len(items)} sản phẩm")
        self.lbl_warn.configure(text=f"⚠️ {low} SP sắp hết" if low else "")

    def _sel(self):
        sel = self.tree.selection()

        if not sel:
            messagebox.showwarning(
                "Chưa chọn",
                "Vui lòng chọn sản phẩm!"
            )
            return None

        ma_sp = int(sel[0])

        # lấy full dữ liệu từ DB
        return svc.get_by_id(ma_sp)

    def _add(self):    ProductDialog(self,None,self._load)
    def _edit(self):
        p = self._sel()
        if p: ProductDialog(self,p,self._load)
    def _delete(self):
        p = self._sel()
        if p and messagebox.askyesno("Xác nhận",f"Ẩn sản phẩm «{p.ten_sp}»?"):
            ok,msg = svc.delete(p.ma_sp)
            (messagebox.showinfo if ok else messagebox.showerror)("Kết quả",msg)
            if ok: self._load()

    def _show_preview(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return

        ma_sp = int(sel[0])
        p = svc.get_by_id(ma_sp)

        if not p:
            return

        self.preview_name.configure(text=p.ten_sp)

        status = (
            "⚠️ Sắp hết hàng"
            if p.ton_kho <= 10 else
            "✅ Còn hàng"
        )

        self.preview_info.configure(
            text=(
                f"Mã SP: {p.ma_code}\n\n"
                f"Loại: {p.ten_loai}\n"
                f"Đơn vị: {p.don_vi}\n\n"
                f"Giá bán: {p.fmt_gia_ban()}\n"
                f"Tồn kho: {p.ton_kho}\n\n"
                f"Trạng thái: {status}"
            )
        )

        try:
            from backend.database.connection import get_connection

            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT hinh_anh FROM san_pham WHERE ma_sp=%s",
                (ma_sp,)
            )

            row = cur.fetchone()
            conn.close()

            if row and row[0] and os.path.exists(row[0]):
                img = Image.open(row[0]).convert("RGB")
                img.thumbnail((180, 180))

                ck = ctk.CTkImage(
                    light_image=img,
                    size=(180, 180)
                )

                self.preview_img.configure(
                    image=ck,
                    text=""
                )

                self.preview_img._ref = ck

            else:
                self.preview_img.configure(
                    image=None,
                    text="📷\nChưa có ảnh"
                )

        except Exception as e:
            print(e)


class ProductDialog(ctk.CTkToplevel):
    def __init__(self,parent,product,callback):
        super().__init__(parent)
        self.product=product; self.callback=callback; self._img_path=None
        self.title("Thêm sản phẩm" if not product else "Sửa sản phẩm")
        self.geometry("560x820"); self.resizable(False,False)
        self.configure(fg_color=CARD); self.grab_set()
        self.after(100, lambda: self.focus())
        self._build()
        if product: self._fill()

    def _build(self):
        hdr = ctk.CTkFrame(self,fg_color=PRIMARY,corner_radius=0,height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr,
            text="➕  Thêm sản phẩm mới" if not self.product else "✏️  Sửa sản phẩm",
            font=ctk.CTkFont(size=FS_LG,weight="bold"),text_color="white").pack(expand=True)

        body = ctk.CTkFrame(self,fg_color=CARD)
        body.pack(fill="both",expand=True,padx=SP_XL,pady=SP_MD)

        def f(label,attr,placeholder=""):
            ctk.CTkLabel(body,text=label,anchor="w",
                font=ctk.CTkFont(size=FS_SM,weight="bold"),text_color=TEXT_SECOND).pack(fill="x",pady=(8,2))
            e = ctk.CTkEntry(body,height=BTN_MD,font=ctk.CTkFont(size=FS_MD),
                placeholder_text=placeholder,fg_color=CARD,border_color=BORDER,corner_radius=RADIUS_SM)
            e.pack(fill="x"); setattr(self,attr,e)

        f("Mã sản phẩm *","e_code","VD: SP001")
        f("Tên sản phẩm *","e_name","VD: Bút bi Thiên Long")
        f("Đơn vị tính","e_unit","cái / hộp / ram...")

        row = ctk.CTkFrame(body,fg_color=CARD); row.pack(fill="x",pady=(8,0))
        for txt,attr,side,pad in [("Giá nhập (đ)","e_cost","left",(0,6)),("Giá bán (đ) *","e_price","right",(6,0))]:
            col = ctk.CTkFrame(row,fg_color=CARD); col.pack(side=side,fill="x",expand=True,padx=pad)
            ctk.CTkLabel(col,text=txt,anchor="w",font=ctk.CTkFont(size=FS_SM,weight="bold"),text_color=TEXT_SECOND).pack(fill="x",pady=(0,2))
            e = ctk.CTkEntry(col,height=BTN_MD,font=ctk.CTkFont(size=FS_MD),placeholder_text="0",
                fg_color=CARD,border_color=BORDER,corner_radius=RADIUS_SM); e.pack(fill="x")
            setattr(self,attr,e)

        f("Tồn kho","e_stock","0")

        ctk.CTkLabel(body,text="Loại sản phẩm",anchor="w",
            font=ctk.CTkFont(size=FS_SM,weight="bold"),text_color=TEXT_SECOND).pack(fill="x",pady=(8,2))
        cats = svc.get_categories()
        self._cat_map = {c["ten"]:c["ma"] for c in cats}
        self.cmb_cat = ctk.CTkComboBox(body,values=[c["ten"] for c in cats] if cats else ["(Chưa có loại)"],
            height=BTN_MD,font=ctk.CTkFont(size=FS_MD),fg_color=CARD,border_color=BORDER,corner_radius=RADIUS_SM)
        self.cmb_cat.pack(fill="x")

        # Ảnh
        ctk.CTkFrame(body,fg_color=BORDER,height=1).pack(fill="x",pady=(12,0))
        ctk.CTkLabel(body,text="🖼️  Ảnh sản phẩm (tùy chọn)",anchor="w",
            font=ctk.CTkFont(size=FS_SM,weight="bold"),text_color=TEXT_SECOND).pack(fill="x",pady=(8,4))
        img_row = ctk.CTkFrame(body,fg_color=CARD); img_row.pack(fill="x")
        self.img_prev = ctk.CTkLabel(img_row,text="📷\nChưa có",width=80,height=80,
            fg_color=BG,corner_radius=RADIUS_SM,font=ctk.CTkFont(size=FS_XS),text_color=TEXT_GRAY)
        self.img_prev.pack(side="left",padx=(0,SP_MD))
        col2 = ctk.CTkFrame(img_row,fg_color=CARD); col2.pack(side="left",fill="x",expand=True)
        self.lbl_img = ctk.CTkLabel(col2,text="Chưa chọn ảnh",font=ctk.CTkFont(size=FS_XS),text_color=TEXT_GRAY,anchor="w")
        self.lbl_img.pack(anchor="w",pady=(0,4))
        r2 = ctk.CTkFrame(col2,fg_color=CARD); r2.pack(anchor="w")
        make_btn(r2,"Chọn ảnh",self._pick,"ghost",height=BTN_SM,icon="📂").pack(side="left",padx=(0,6))
        make_btn(r2,"Xóa ảnh", self._clear,"danger",height=BTN_SM,icon="🗑").pack(side="left")

        ctk.CTkFrame(body,fg_color=BORDER,height=1).pack(fill="x",pady=(12,8))
        make_btn(body,"Lưu sản phẩm",self._save,"primary",height=BTN_LG,icon="💾").pack(fill="x")
        if self.product: self.e_code.configure(state="disabled")

    def _fill(self):
        p = self.product
        self.e_code.configure(state="normal"); self.e_code.insert(0,p.ma_code); self.e_code.configure(state="disabled")
        self.e_name.insert(0,p.ten_sp); self.e_unit.insert(0,p.don_vi or "")
        self.e_cost.insert(0,str(int(p.gia_nhap))); self.e_price.insert(0,str(int(p.gia_ban)))
        self.e_stock.insert(0,str(p.ton_kho))
        if p.ten_loai and p.ten_loai in self._cat_map: self.cmb_cat.set(p.ten_loai)

    def _pick(self):
        path = filedialog.askopenfilename(title="Chọn ảnh",
            filetypes=[("Ảnh","*.jpg *.jpeg *.png *.gif *.bmp"),("Tất cả","*.*")])
        if not path: return
        self._img_path = path; self.lbl_img.configure(text=os.path.basename(path))
        try:
            from PIL import Image
            img = Image.open(path).convert("RGB"); img.thumbnail((80,80))
            ck = ctk.CTkImage(light_image=img,size=(80,80))
            self.img_prev.configure(image=ck,text=""); self.img_prev._ref=ck
        except Exception: pass

    def _clear(self):
        self._img_path=""; self.img_prev.configure(text="📷\nChưa có",image=None)
        self.lbl_img.configure(text="Chưa chọn ảnh")

    def _save(self):
        try:
            p = Product(ma_sp=self.product.ma_sp if self.product else None,
                ma_code=self.e_code.get().strip(), ten_sp=self.e_name.get().strip(),
                don_vi=self.e_unit.get().strip(),
                gia_nhap=float(self.e_cost.get() or 0), gia_ban=float(self.e_price.get() or 0),
                ton_kho=int(self.e_stock.get() or 0),
                ma_loai=self._cat_map.get(self.cmb_cat.get()))
        except ValueError:
            messagebox.showerror("Lỗi","Giá và tồn kho phải là số!"); return
        ok,msg = svc.update(p) if self.product else svc.add(p)
        if not ok: messagebox.showerror("Lỗi",msg); return
        if self._img_path is not None:
            _save_img(p.ma_sp or _last_id(), self._img_path)
        messagebox.showinfo("Thành công",msg)
        self.callback(); self.destroy()


def _save_img(ma_sp,src):
    try:
        import shutil
        from backend.database.connection import get_connection
        conn=get_connection(); cur=conn.cursor()
        if src=="":
            cur.execute("UPDATE san_pham SET hinh_anh=NULL WHERE ma_sp=%s",(ma_sp,))
        else:
            ext=os.path.splitext(src)[1].lower() or ".jpg"
            dst=os.path.join(IMG_DIR,f"sp_{ma_sp}{ext}"); shutil.copy2(src,dst)
            cur.execute("UPDATE san_pham SET hinh_anh=%s WHERE ma_sp=%s",(dst,ma_sp))
        conn.commit(); conn.close()
    except Exception as e: print(f"[IMG]{e}")

def _last_id():
    try:
        from backend.database.connection import get_connection
        conn=get_connection(); cur=conn.cursor()
        cur.execute("SELECT ma_sp FROM san_pham ORDER BY ma_sp DESC LIMIT 1")
        row=cur.fetchone(); conn.close(); return row[0] if row else 0
    except: return 0
