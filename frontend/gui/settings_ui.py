# frontend/gui/settings_ui.py — Cài đặt cửa hàng + tích điểm + logo
import os, customtkinter as ctk
from tkinter import messagebox, filedialog
from frontend.gui.theme import (
    make_btn, page_header, make_card, divider,
    SP_SM, SP_MD, SP_LG, SP_XL,
    FS_XS, FS_SM, FS_MD, FS_LG,
    BTN_SM, BTN_MD, BTN_LG, RADIUS_SM,
    PRIMARY, SUCCESS, DANGER,
    CARD, BORDER, BG, TEXT_PRIMARY, TEXT_SECOND, TEXT_GRAY,
)
from backend.modules.config_service import get_all, set_val


LOGO_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "assets", "logo.png")


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._logo_path_new = None
        self._build_ui()
        self._load()

    def _build_ui(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=SP_LG, pady=(SP_LG, SP_SM))
        page_header(tb, "⚙️  Cài đặt hệ thống",
                    "Thông tin cửa hàng, hóa đơn và chính sách khách hàng"
                    ).pack(side="left")
        make_btn(tb, "Lưu tất cả", self._save_all,
                 "success", icon="💾").pack(side="right")

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True,
                  padx=SP_MD, pady=(0, SP_MD))
        self._build_store(main)
        self._build_policy(main)

    # ── Cột trái: Thông tin cửa hàng ─────────────────────────
    def _build_store(self, parent):
        frm = make_card(parent)
        frm.pack(side="left", fill="both", expand=True,
                 padx=(0, SP_SM))

        ctk.CTkLabel(frm, text="🏪  Thông tin cửa hàng",
                     font=ctk.CTkFont(size=FS_LG, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=SP_MD, pady=(SP_MD, 4))
        divider(frm).pack(fill="x", padx=SP_MD)

        body = ctk.CTkFrame(frm, fg_color=CARD)
        body.pack(fill="both", expand=True,
                  padx=SP_XL, pady=SP_MD)

        def field(label, attr, placeholder="", note=""):
            ctk.CTkLabel(body, text=label, anchor="w",
                         font=ctk.CTkFont(size=FS_SM, weight="bold"),
                         text_color=TEXT_SECOND).pack(
                fill="x", pady=(SP_SM, 2))
            e = ctk.CTkEntry(body, height=BTN_MD,
                              placeholder_text=placeholder,
                              fg_color=CARD, border_color=BORDER,
                              corner_radius=RADIUS_SM)
            e.pack(fill="x")
            if note:
                ctk.CTkLabel(body, text=note, anchor="w",
                             font=ctk.CTkFont(size=FS_XS),
                             text_color=TEXT_GRAY).pack(fill="x")
            setattr(self, attr, e)

        field("Tên cửa hàng *", "e_ten", "Cửa Hàng VPP ABC",
              "Hiển thị trên hóa đơn PDF")
        field("Địa chỉ",        "e_dc",  "Số nhà, đường, quận, TP")
        field("Số điện thoại",  "e_sdt", "028 1234 5678")
        field("Email",          "e_email","vppabc@gmail.com")
        field("Website",        "e_web", "www.vppabc.vn")
        field("Mã số thuế",     "e_mst", "0123456789")

        # Logo
        divider(body).pack(fill="x", pady=(SP_MD, SP_SM))
        ctk.CTkLabel(body, text="🖼️  Logo cửa hàng (PNG)",
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color=TEXT_SECOND).pack(anchor="w")

        logo_row = ctk.CTkFrame(body, fg_color=CARD)
        logo_row.pack(fill="x", pady=(SP_SM, 0))

        self.lbl_logo_prev = ctk.CTkLabel(
            logo_row, text="📷\nChưa có logo",
            width=80, height=80,
            fg_color=BG, corner_radius=RADIUS_SM,
            font=ctk.CTkFont(size=FS_XS),
            text_color=TEXT_GRAY)
        self.lbl_logo_prev.pack(side="left", padx=(0, SP_MD))

        btn_col = ctk.CTkFrame(logo_row, fg_color=CARD)
        btn_col.pack(side="left", fill="x", expand=True)
        self.lbl_logo_name = ctk.CTkLabel(
            btn_col, text="Kích thước tốt nhất: 200×200px",
            font=ctk.CTkFont(size=FS_XS),
            text_color=TEXT_GRAY, anchor="w")
        self.lbl_logo_name.pack(anchor="w", pady=(0, 4))
        make_btn(btn_col, "Chọn logo", self._pick_logo,
                 "ghost", height=BTN_SM, icon="📂").pack(anchor="w")

    # ── Cột phải: Chính sách khách hàng ─────────────────────
    def _build_policy(self, parent):
        frm = make_card(parent)
        frm.configure(width=380)
        frm.pack(side="right", fill="y")
        frm.pack_propagate(False)

        ctk.CTkLabel(frm, text="🎯  Chính sách tích điểm",
                     font=ctk.CTkFont(size=FS_LG, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=SP_MD, pady=(SP_MD, 4))
        divider(frm).pack(fill="x", padx=SP_MD)

        body = ctk.CTkFrame(frm, fg_color=CARD)
        body.pack(fill="both", expand=True,
                  padx=SP_LG, pady=SP_MD)

        def field(label, attr, placeholder="", note=""):
            ctk.CTkLabel(body, text=label, anchor="w",
                         font=ctk.CTkFont(size=FS_SM, weight="bold"),
                         text_color=TEXT_SECOND).pack(
                fill="x", pady=(SP_SM, 2))
            e = ctk.CTkEntry(body, height=BTN_MD,
                              placeholder_text=placeholder,
                              fg_color=CARD, border_color=BORDER,
                              corner_radius=RADIUS_SM)
            e.pack(fill="x")
            if note:
                ctk.CTkLabel(body, text=note, anchor="w",
                             font=ctk.CTkFont(size=FS_XS),
                             text_color=TEXT_GRAY).pack(fill="x")
            setattr(self, attr, e)

        field("Số tiền tích 1 điểm (đ)",
              "e_tl_diem", "10000",
              "VD: 10000 = cứ 10.000đ mua được 1 điểm")
        field("1 điểm = bao nhiêu đồng giảm giá",
              "e_doi_diem", "1000",
              "VD: 1 điểm = giảm 1.000đ khi thanh toán")
        field("Ngưỡng cảnh báo tồn kho (SP)",
              "e_nguong", "10",
              "SP có tồn kho ≤ ngưỡng này sẽ hiển thị cảnh báo")

        divider(body).pack(fill="x", pady=(SP_MD, SP_SM))
        ctk.CTkLabel(body, text="🏅  Ngưỡng xếp hạng khách hàng",
                     font=ctk.CTkFont(size=FS_MD, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")

        for label, attr, placeholder in [
            ("Hạng Bạc (đ chi tiêu)",     "e_ng_bac",    "500000"),
            ("Hạng Vàng (đ chi tiêu)",    "e_ng_vang",   "2000000"),
            ("Hạng Bạch Kim (đ chi tiêu)","e_ng_bk",     "5000000"),
        ]:
            field(label, attr, placeholder)

        # Preview hạng
        divider(body).pack(fill="x", pady=(SP_MD, SP_SM))
        ctk.CTkLabel(body, text="📋  Xem trước hạng KH:",
                     font=ctk.CTkFont(size=FS_SM, weight="bold"),
                     text_color=TEXT_SECOND).pack(anchor="w")

        for icon, hang, color in [
            ("⭐", "Thường",   TEXT_GRAY),
            ("🥈", "Bạc",     "#607D8B"),
            ("🥇", "Vàng",    "#B8860B"),
            ("💎", "Bạch Kim","#6A1B9A"),
        ]:
            r = ctk.CTkFrame(body, fg_color=CARD)
            r.pack(fill="x", pady=1)
            ctk.CTkLabel(r, text=f"{icon}  {hang}",
                         font=ctk.CTkFont(size=FS_SM),
                         text_color=color).pack(side="left", padx=4, pady=3)

    # ── Load / Save ───────────────────────────────────────────
    def _load(self):
        cfg = get_all()
        mapping = [
            ("ten_cua_hang",       "e_ten"),
            ("dia_chi",            "e_dc"),
            ("so_dien_thoai",      "e_sdt"),
            ("email",              "e_email"),
            ("website",            "e_web"),
            ("ma_so_thue",         "e_mst"),
            ("ty_le_tich_diem",    "e_tl_diem"),
            ("doi_diem",           "e_doi_diem"),
            ("canh_bao_ton_kho",   "e_nguong"),
            ("nguong_hang_bac",    "e_ng_bac"),
            ("nguong_hang_vang",   "e_ng_vang"),
            ("nguong_hang_bachkim","e_ng_bk"),
        ]
        for key, attr in mapping:
            e = getattr(self, attr, None)
            if e:
                e.delete(0, "end")
                e.insert(0, cfg.get(key, ""))

        # Load logo
        if os.path.exists(LOGO_PATH):
            self._show_logo_preview(LOGO_PATH)

    def _save_all(self):
        mapping = [
            ("ten_cua_hang",       "e_ten"),
            ("dia_chi",            "e_dc"),
            ("so_dien_thoai",      "e_sdt"),
            ("email",              "e_email"),
            ("website",            "e_web"),
            ("ma_so_thue",         "e_mst"),
            ("ty_le_tich_diem",    "e_tl_diem"),
            ("doi_diem",           "e_doi_diem"),
            ("canh_bao_ton_kho",   "e_nguong"),
            ("nguong_hang_bac",    "e_ng_bac"),
            ("nguong_hang_vang",   "e_ng_vang"),
            ("nguong_hang_bachkim","e_ng_bk"),
        ]
        for key, attr in mapping:
            e = getattr(self, attr, None)
            if e:
                set_val(key, e.get().strip())

        # Lưu logo
        if self._logo_path_new:
            import shutil, os as _os
            _os.makedirs(_os.path.dirname(LOGO_PATH), exist_ok=True)
            shutil.copy2(self._logo_path_new, LOGO_PATH)

        messagebox.showinfo("✅ Đã lưu",
                            "Cài đặt đã được lưu thành công!")

    def _pick_logo(self):
        path = filedialog.askopenfilename(
            title="Chọn logo cửa hàng",
            filetypes=[("Ảnh PNG", "*.png"),
                       ("Ảnh JPG", "*.jpg *.jpeg"),
                       ("Tất cả",  "*.*")])
        if not path:
            return
        self._logo_path_new = path
        self.lbl_logo_name.configure(
            text=os.path.basename(path))
        self._show_logo_preview(path)

    def _show_logo_preview(self, path: str):
        try:
            from PIL import Image
            img = Image.open(path).convert("RGBA")
            img.thumbnail((80, 80))
            ck = ctk.CTkImage(light_image=img, size=(80, 80))
            self.lbl_logo_prev.configure(image=ck, text="")
            self.lbl_logo_prev._img_ref = ck
        except Exception:
            self.lbl_logo_prev.configure(text="(Lỗi ảnh)", image=None)
