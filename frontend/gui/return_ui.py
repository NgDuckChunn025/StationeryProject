# frontend/gui/return_ui.py — Màn hình Trả hàng
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from frontend.gui.theme import (
    apply_treeview_style, make_btn, page_header, make_card,
    SP_SM, SP_MD, SP_LG, SP_XL,
    FS_XS, FS_SM, FS_MD, FS_LG,
    BTN_SM, BTN_MD, BTN_LG, RADIUS_SM,
    PRIMARY, PRIMARY_LIGHT, DANGER, DANGER_LIGHT, SUCCESS,
    CARD, BORDER, TEXT_PRIMARY, TEXT_SECOND, TEXT_GRAY,
)
from backend.modules import return_service as rsvc


class ReturnFrame(ctk.CTkFrame):
    """Màn hình chính quản lý trả hàng."""
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self._build_ui()
        self._load_history()

    def _build_ui(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=SP_LG, pady=(SP_LG, SP_SM))
        page_header(tb, "↩️  Trả hàng & Hoàn tiền",
                    "Tạo phiếu trả hàng từ hóa đơn đã bán").pack(side="left")
        make_btn(tb, "Tạo phiếu trả", self._new_return,
                 "danger", icon="➕").pack(side="right")

        # Lịch sử phiếu trả
        tbl = make_card(self)
        tbl.pack(fill="both", expand=True,
                 padx=SP_LG, pady=(0, SP_LG))

        style  = ttk.Style()
        tv     = apply_treeview_style(style)
        cols   = ("Mã phiếu", "Mã HĐ gốc", "Khách hàng",
                  "Nhân viên", "Ngày trả", "Tổng hoàn", "Lý do")
        self.tree = ttk.Treeview(tbl, columns=cols,
                                  show="headings", style=tv)
        cfg = [
            ("Mã phiếu",   80,  "center"),
            ("Mã HĐ gốc",  90,  "center"),
            ("Khách hàng", 160, "center"),
            ("Nhân viên",  130, "center"),
            ("Ngày trả",   130, "center"),
            ("Tổng hoàn",  120, "center"),
            ("Lý do",      200, "center"),
        ]
        for col, w, a in cfg:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=w, anchor=a,
                             minwidth=w, stretch=False)
        self.tree.tag_configure("odd",  background="#F7FAFF")
        self.tree.tag_configure("even", background="#FFFFFF")
        sy = ttk.Scrollbar(tbl, orient="vertical",
                            command=self.tree.yview,
                            style="VPP.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=sy.set)
        self.tree.pack(side="left", fill="both", expand=True,
                       padx=(SP_SM,0), pady=SP_SM)
        sy.pack(side="right", fill="y", pady=SP_SM, padx=(0,4))

    def _load_history(self):
        rows = rsvc.get_return_history()
        for r in self.tree.get_children(): self.tree.delete(r)
        for i, row in enumerate(rows):
            ma_pt, ma_hd, kh, nv, ngay, tong, ly_do, httt = row
            tag = "odd" if i%2 else "even"
            self.tree.insert("", "end",
                             values=(f"#{ma_pt:04d}",
                                     f"#{ma_hd:04d}", kh, nv,
                                     str(ngay)[:16],
                                     f"{float(tong or 0):,.0f}đ",
                                     ly_do or ""),
                             tags=(tag,))

    def _new_return(self):
        ReturnDialog(self, None, self.user, self._load_history)


class ReturnDialog(ctk.CTkToplevel):
    """Dialog tạo phiếu trả hàng."""
    def __init__(self, parent, ma_hd_init, user_or_callback,
                 callback=None):
        super().__init__(parent)
        # Hỗ trợ cả 2 cách gọi
        if callable(user_or_callback) and callback is None:
            self.user     = None
            self.callback = user_or_callback
        else:
            self.user     = user_or_callback
            self.callback = callback

        self.ma_nv     = (self.user["ma_nv"]
                          if self.user else 1)
        self._hd_data  = None
        self._items_tra = []   # list dict {ma_sp, ten_sp, don_gia, sl_max, sl_tra, e_sl}

        self.title("Tạo phiếu trả hàng")
        self.geometry("680x620")
        self.resizable(False, True)
        self.configure(fg_color=CARD)
        self.grab_set()
        self._build()
        if ma_hd_init:
            self.ent_mahd.insert(0, str(ma_hd_init))
            self._load_hd()

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=DANGER,
                            corner_radius=0, height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="↩️  Tạo phiếu trả hàng",
                     font=ctk.CTkFont(size=FS_LG, weight="bold"),
                     text_color="white").pack(expand=True)

        body = ctk.CTkFrame(self, fg_color=CARD)
        body.pack(fill="both", expand=True,
                  padx=SP_XL, pady=SP_MD)

        # Tìm hóa đơn
        row0 = ctk.CTkFrame(body, fg_color=CARD)
        row0.pack(fill="x")
        ctk.CTkLabel(row0, text="Mã hóa đơn gốc *", anchor="w",
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color=TEXT_SECOND).pack(
            side="left", padx=(0, SP_SM))
        self.ent_mahd = ctk.CTkEntry(
            row0, width=100, height=BTN_MD,
            placeholder_text="#0001",
            fg_color=CARD, border_color=BORDER,
            corner_radius=RADIUS_SM)
        self.ent_mahd.pack(side="left")
        make_btn(row0, "Tải hóa đơn", self._load_hd,
                 "primary", height=BTN_MD, icon="🔍").pack(
            side="left", padx=SP_SM)

        # Thông tin hóa đơn
        self.info_f = ctk.CTkFrame(body, fg_color=PRIMARY_LIGHT,
                                    corner_radius=RADIUS_SM)
        self.info_f.pack(fill="x", pady=(SP_SM, 0))
        self.lbl_info = ctk.CTkLabel(
            self.info_f,
            text="Nhập mã hóa đơn và nhấn Tải hóa đơn",
            font=ctk.CTkFont(size=FS_SM),
            text_color=TEXT_GRAY, justify="left")
        self.lbl_info.pack(anchor="w", padx=SP_MD, pady=SP_SM)

        # Bảng chọn SP trả
        ctk.CTkLabel(body, text="Chọn sản phẩm cần trả:", anchor="w",
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color=TEXT_SECOND).pack(
            fill="x", pady=(SP_MD, 4))

        self.items_frame = ctk.CTkFrame(body, fg_color=CARD,
                                         border_width=1,
                                         border_color=BORDER,
                                         corner_radius=RADIUS_SM)
        self.items_frame.pack(fill="x")

        # Lý do
        ctk.CTkLabel(body, text="Lý do trả hàng:", anchor="w",
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color=TEXT_SECOND).pack(
            fill="x", pady=(SP_MD, 4))
        self.ent_lydo = ctk.CTkEntry(
            body, height=BTN_MD,
            placeholder_text="Sản phẩm lỗi / không đúng yêu cầu...",
            fg_color=CARD, border_color=BORDER,
            corner_radius=RADIUS_SM)
        self.ent_lydo.pack(fill="x")

        # Hình thức hoàn
        row_ht = ctk.CTkFrame(body, fg_color=CARD)
        row_ht.pack(fill="x", pady=(SP_SM, 0))
        ctk.CTkLabel(row_ht, text="Hình thức hoàn:",
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color=TEXT_SECOND).pack(side="left")
        self.cmb_httt = ctk.CTkComboBox(
            row_ht,
            values=["Tiền mặt", "Chuyển khoản", "Tích vào điểm KH"],
            height=BTN_MD, width=200,
            fg_color=CARD, border_color=BORDER,
            corner_radius=RADIUS_SM)
        self.cmb_httt.pack(side="left", padx=SP_MD)
        self.cmb_httt.set("Tiền mặt")

        # Tổng hoàn
        self.lbl_tong = ctk.CTkLabel(
            body, text="Tổng hoàn: 0đ",
            font=ctk.CTkFont(size=FS_LG, weight="bold"),
            text_color=DANGER)
        self.lbl_tong.pack(anchor="e", pady=(SP_SM, 0))

        # Nút Lưu
        ctk.CTkFrame(body, fg_color=BORDER, height=1).pack(
            fill="x", pady=(SP_MD, SP_SM))
        make_btn(body, "Lưu phiếu trả hàng", self._save,
                 "danger", height=BTN_LG, icon="💾").pack(fill="x")

    def _load_hd(self):
        txt = self.ent_mahd.get().strip().lstrip("#")
        if not txt:
            return
        try:
            ma_hd = int(txt)
        except ValueError:
            messagebox.showerror("Lỗi", "Mã HĐ phải là số nguyên!")
            return

        data = rsvc.get_invoice_for_return(ma_hd)
        if not data:
            messagebox.showerror("Không tìm thấy",
                                  f"Không có hóa đơn #{ma_hd:04d}!")
            return

        self._hd_data = data
        self.lbl_info.configure(
            text=f"HĐ #{data['ma_hd']:04d}  |  Khách: {data['ten_kh']}  "
                 f"|  Thanh toán: {data['thanh_toan']:,.0f}đ")

        # Dựng rows chọn SP
        for w in self.items_frame.winfo_children():
            w.destroy()

        # Header
        hdr_row = ctk.CTkFrame(self.items_frame,
                                fg_color=PRIMARY, corner_radius=0)
        hdr_row.pack(fill="x")
        for txt, w in [("Tên sản phẩm", 240),
                       ("Đơn giá", 90), ("Đã mua", 60), ("Trả SL", 80)]:
            ctk.CTkLabel(hdr_row, text=txt, width=w,
                         font=ctk.CTkFont(size=FS_SM, weight="bold"),
                         text_color="white").pack(
                side="left", padx=4, pady=6)

        self._items_tra.clear()
        for item in data["items"]:
            row = ctk.CTkFrame(self.items_frame, fg_color=CARD)
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=item["ten_sp"], width=240,
                         font=ctk.CTkFont(size=FS_SM),
                         anchor="w").pack(side="left", padx=4, pady=4)
            ctk.CTkLabel(row,
                         text=f"{item['don_gia']:,.0f}đ",
                         width=90, anchor="e",
                         font=ctk.CTkFont(size=FS_SM)).pack(
                side="left", padx=4)
            ctk.CTkLabel(row, text=str(item["so_luong"]),
                         width=60, anchor="center",
                         font=ctk.CTkFont(size=FS_SM)).pack(
                side="left", padx=4)
            e = ctk.CTkEntry(row, width=70, height=28,
                              placeholder_text="0",
                              fg_color=CARD, border_color=BORDER,
                              corner_radius=RADIUS_SM)
            e.insert(0, "0")
            e.pack(side="left", padx=4)
            e.bind("<KeyRelease>", lambda _: self._calc_total())
            self._items_tra.append({
                "ma_sp"    : item["ma_sp"],
                "ten_sp"   : item["ten_sp"],
                "don_gia"  : item["don_gia"],
                "sl_max"   : item["so_luong"],
                "e_sl"     : e,
            })

    def _calc_total(self):
        tong = 0.0
        for it in self._items_tra:
            try:
                sl = int(it["e_sl"].get() or 0)
                sl = max(0, min(sl, it["sl_max"]))
                tong += sl * it["don_gia"]
            except Exception:
                pass
        self.lbl_tong.configure(text=f"Tổng hoàn: {tong:,.0f}đ")

    def _save(self):
        if not self._hd_data:
            messagebox.showwarning("Chưa tải HĐ",
                                   "Vui lòng tải hóa đơn trước!")
            return
        items_tra = []
        for it in self._items_tra:
            try:
                sl = int(it["e_sl"].get() or 0)
            except Exception:
                sl = 0
            if sl > it["sl_max"]:
                messagebox.showwarning(
                    "Số lượng vượt",
                    f"SP «{it['ten_sp']}»: "
                    f"trả tối đa {it['sl_max']}!")
                return
            if sl > 0:
                items_tra.append({
                    "ma_sp"       : it["ma_sp"],
                    "so_luong_tra": sl,
                    "don_gia"     : it["don_gia"],
                })
        if not items_tra:
            messagebox.showwarning("Chưa chọn SP",
                                   "Nhập số lượng trả ≥ 1!")
            return
        ly_do = self.ent_lydo.get().strip()
        httt  = self.cmb_httt.get()

        ok, result = rsvc.create_return(
            self._hd_data["ma_hd"], self.ma_nv,
            items_tra, ly_do, httt)
        if ok:
            messagebox.showinfo(
                "Thành công",
                f"Đã tạo phiếu trả #{result:04d}!\n"
                f"Tồn kho đã được hoàn lại.")
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Lỗi", str(result))
