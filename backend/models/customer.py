# backend/models/customer.py
# ================================================================
# Class Customer (KhachHang) — đối tượng nghiệp vụ khách hàng
# ================================================================


class Customer:
    def __init__(self,
                 ma_kh=None,
                 ten_kh="",
                 so_dt="",
                 dia_chi="",
                 email="",
                 diem_tich_luy=0,
                 hang_khach_hang="Thường",
                 tong_chi_tieu=0):
        self.ma_kh         = ma_kh
        self.ten_kh        = ten_kh.strip() if ten_kh else ""
        self.so_dt         = so_dt.strip()  if so_dt  else ""
        self.dia_chi       = dia_chi.strip() if dia_chi else ""
        self.email         = email.strip()   if email  else ""
        self.diem_tich_luy = int(diem_tich_luy or 0)
        self.hang_khach_hang = hang_khach_hang
        self.tong_chi_tieu = float(tong_chi_tieu or 0)

    # ---- Validation ----
    def validate(self) -> tuple[bool, str]:
        if not self.ten_kh:
            return False, "Tên khách hàng không được trống!"
        if self.so_dt and not self.so_dt.isdigit():
            return False, "Số điện thoại chỉ được chứa chữ số!"
        return True, ""

    # ---- Display ----
    def to_table_row(self):
        """Tuple hiển thị trên Treeview."""
        return (
            self.ma_kh,
            self.ten_kh,
            self.so_dt or "—",
            self.dia_chi or "—",
            self.hang_khach_hang,
            f"{self.diem_tich_luy:,}",
            f"{self.tong_chi_tieu:,.0f}đ",
        )

    @staticmethod
    def from_row(row):
        """
        Tạo Customer từ dòng query.
        row = (ma_kh, ten_kh, so_dt, dia_chi, email, diem_tich_luy)
        """
        return Customer(
            ma_kh         = row[0],
            ten_kh        = row[1] or "",
            so_dt         = row[2] or "",
            dia_chi       = row[3] or "",
            email         = row[4] or "",
            diem_tich_luy=row[5] or 0,
            hang_khach_hang=row[6] or "Thường",
            tong_chi_tieu=row[7] or 0,
        )

    def __str__(self):
        return f"[KH#{self.ma_kh}] {self.ten_kh} | {self.so_dt}"