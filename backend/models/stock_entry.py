# backend/models/stock_entry.py
# ================================================================
# Class StockEntry (PhieuNhap) & StockItem (ChiTietPhieuNhap)
# ================================================================

from datetime import datetime


class StockItem:
    """Một dòng trong phiếu nhập kho."""
    def __init__(self, ma_sp, ten_sp, don_gia, so_luong):
        self.ma_sp    = ma_sp
        self.ten_sp   = ten_sp
        self.don_gia  = float(don_gia or 0)
        self.so_luong = int(so_luong or 0)

    @property
    def thanh_tien(self):
        return self.don_gia * self.so_luong

    def to_table_row(self):
        return (
            self.ten_sp,
            f"{self.don_gia:,.0f}đ",
            self.so_luong,
            f"{self.thanh_tien:,.0f}đ",
        )

    def to_dict(self):
        return {
            "ma_sp"   : self.ma_sp,
            "so_luong": self.so_luong,
            "don_gia" : self.don_gia,
        }


class StockEntry:
    """Phiếu nhập kho — chứa danh sách StockItem."""

    def __init__(self, ma_nv, ten_nv, ma_ncc=None, ten_ncc=""):
        self.ma_phieu  = None
        self.ma_nv     = ma_nv
        self.ten_nv    = ten_nv
        self.ma_ncc    = ma_ncc
        self.ten_ncc   = ten_ncc
        self.ngay_nhap = datetime.now()
        self.ghi_chu   = ""
        self.items: list[StockItem] = []

    # ---- Quản lý items ----
    def add_item(self, ma_sp, ten_sp, don_gia, so_luong=1):
        """Thêm sản phẩm; nếu đã có thì cộng số lượng."""
        for item in self.items:
            if item.ma_sp == ma_sp:
                item.so_luong += so_luong
                return
        self.items.append(StockItem(ma_sp, ten_sp, don_gia, so_luong))

    def remove_item(self, ma_sp):
        self.items = [i for i in self.items if i.ma_sp != ma_sp]

    def clear(self):
        self.items.clear()

    # ---- Tính tiền ----
    @property
    def tong_tien(self):
        return sum(i.thanh_tien for i in self.items)

    @property
    def so_dong(self):
        return len(self.items)

    # ---- Xuất dict để lưu DB ----
    def to_dict(self):
        return {
            "ma_ncc"  : self.ma_ncc,
            "ma_nv"   : self.ma_nv,
            "tong_tien": self.tong_tien,
            "ghi_chu" : self.ghi_chu,
            "items"   : [i.to_dict() for i in self.items],
        }

    def __str__(self):
        return (f"Phiếu #{self.ma_phieu or '?'} | {self.ten_ncc or 'Chưa chọn NCC'} "
                f"| {self.tong_tien:,.0f}đ | {self.so_dong} dòng")