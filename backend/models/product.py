# backend/models/product.py
# ================================================================
# Class Product (SanPham) — đối tượng nghiệp vụ sản phẩm
# ================================================================

class Product:
    def __init__(self, ma_sp=None, ma_code="", ten_sp="", ten_loai="",
                 don_vi="", gia_nhap=0, gia_ban=0, ton_kho=0, mo_ta="", ma_loai=None):
        self.ma_sp    = ma_sp
        self.ma_code  = ma_code
        self.ten_sp   = ten_sp
        self.ten_loai = ten_loai
        self.don_vi   = don_vi
        self.gia_nhap = float(gia_nhap or 0)
        self.gia_ban  = float(gia_ban  or 0)
        self.ton_kho  = int(ton_kho    or 0)
        self.mo_ta    = mo_ta
        self.ma_loai  = ma_loai

    # ---- Computed properties ----
    @property
    def loi_nhuan(self):
        return self.gia_ban - self.gia_nhap

    @property
    def ty_le_loi_nhuan(self):
        return round((self.loi_nhuan / self.gia_nhap) * 100, 1) if self.gia_nhap else 0

    @property
    def sap_het(self):
        return self.ton_kho <= 10

    # ---- Format helpers ----
    def fmt_gia_ban(self):
        return f"{self.gia_ban:,.0f}đ"

    def fmt_gia_nhap(self):
        return f"{self.gia_nhap:,.0f}đ"

    def to_table_row(self):
        """Tuple hiển thị trên Treeview."""
        return (self.ma_code, self.ten_sp, self.ten_loai or "",
                self.don_vi or "", self.fmt_gia_nhap(),
                self.fmt_gia_ban(), self.ton_kho)

    @staticmethod
    def from_row(row):
        """
        Tạo Product từ dòng query trả về.
        row = (ma_sp, ma_code, ten_sp, ten_loai, don_vi, gia_nhap, gia_ban, ton_kho, ma_loai)
        """
        return Product(
            ma_sp    = row[0],
            ma_code  = row[1],
            ten_sp   = row[2],
            ten_loai = row[3] or "Chưa phân loại",
            don_vi   = row[4] or "",
            gia_nhap = row[5] or 0,
            gia_ban  = row[6] or 0,
            ton_kho  = row[7] or 0,
            ma_loai  = row[8] if len(row) > 8 else None,
        )

    def __str__(self):
        return f"[{self.ma_code}] {self.ten_sp} | {self.fmt_gia_ban()} | Tồn: {self.ton_kho}"