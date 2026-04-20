# backend/models/invoice.py
# ================================================================
# Class Invoice (HoaDon) & InvoiceItem (ChiTietHoaDon)
# ================================================================

from datetime import datetime


class InvoiceItem:
    """Một dòng trong hóa đơn."""
    def __init__(self, ma_sp, ten_sp, don_gia, so_luong):
        self.ma_sp    = ma_sp
        self.ten_sp   = ten_sp
        self.don_gia  = float(don_gia)
        self.so_luong = int(so_luong)

    @property
    def thanh_tien(self):
        return self.don_gia * self.so_luong

    def to_table_row(self):
        return (self.ten_sp, f"{self.don_gia:,.0f}đ",
                self.so_luong, f"{self.thanh_tien:,.0f}đ")

    def to_dict(self):
        return {"ma_sp": self.ma_sp, "so_luong": self.so_luong, "don_gia": self.don_gia}


class Invoice:
    """Hóa đơn bán hàng — chứa danh sách InvoiceItem."""

    def __init__(self, ma_nv, ten_nv, ma_kh=None, ten_kh="Khách lẻ"):
        self.ma_hd     = None
        self.ma_nv     = ma_nv
        self.ten_nv    = ten_nv
        self.ma_kh     = ma_kh
        self.ten_kh    = ten_kh
        self.ngay_ban  = datetime.now()
        self.giam_gia  = 0.0
        self.hinh_thuc = "Tiền mặt"
        self.items: list[InvoiceItem] = []

    # ---- Quản lý items ----
    def add_item(self, ma_sp, ten_sp, don_gia, so_luong=1):
        """Thêm sản phẩm. Nếu đã có thì cộng dồn số lượng."""
        for item in self.items:
            if item.ma_sp == ma_sp:
                item.so_luong += so_luong
                return
        self.items.append(InvoiceItem(ma_sp, ten_sp, don_gia, so_luong))

    def remove_item(self, ma_sp):
        self.items = [i for i in self.items if i.ma_sp != ma_sp]

    def clear(self):
        self.items.clear()
        self.giam_gia = 0

    # ---- Tính tiền ----
    @property
    def tong_tien(self):
        return sum(i.thanh_tien for i in self.items)

    @property
    def thanh_toan(self):
        return max(0.0, self.tong_tien - self.giam_gia)

    @property
    def so_mon(self):
        return len(self.items)

    # ---- Xuất dict để lưu DB ----
    def to_dict(self):
        return {
            "ma_kh"    : self.ma_kh,
            "ma_nv"    : self.ma_nv,
            "tong_tien": self.tong_tien,
            "giam_gia" : self.giam_gia,
            "thanh_toan": self.thanh_toan,
            "hinh_thuc": self.hinh_thuc,
            "items"    : [i.to_dict() for i in self.items],
        }

    def __str__(self):
        return (f"HĐ #{self.ma_hd or '?'} | {self.ten_kh} | "
                f"{self.thanh_toan:,.0f}đ | {self.so_mon} món")