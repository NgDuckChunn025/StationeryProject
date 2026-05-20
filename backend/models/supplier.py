# backend/models/supplier.py
# ================================================================
# Class Supplier (NhaCungCap) — đối tượng nghiệp vụ nhà cung cấp
# ================================================================


class Supplier:
    def __init__(self, ma_ncc=None, ten_ncc="", nguoi_lh="",
                 dia_chi="", so_dt="", email="",
                 website="", ghi_chu="", trang_thai=1):
        self.ma_ncc   = ma_ncc
        self.ten_ncc  = ten_ncc.strip()  if ten_ncc  else ""
        self.nguoi_lh = nguoi_lh.strip() if nguoi_lh else ""
        self.dia_chi  = dia_chi.strip()  if dia_chi  else ""
        self.so_dt    = so_dt.strip()    if so_dt    else ""
        self.email    = email.strip()    if email    else ""
        self.website  = website.strip()  if website  else ""
        self.ghi_chu  = ghi_chu.strip()  if ghi_chu  else ""
        self.trang_thai = int(trang_thai)

    # ---- Validation ----
    def validate(self) -> tuple[bool, str]:
        if not self.ten_ncc:
            return False, "Tên nhà cung cấp không được trống!"
        if self.so_dt and not self.so_dt.isdigit():
            return False, "Số điện thoại chỉ được chứa chữ số!"
        if self.email and "@" not in self.email:
            return False, "Email không hợp lệ!"
        return True, ""

    # ---- Display ----
    @property
    def trang_thai_str(self):
        return "Hoạt động" if self.trang_thai else "Ngừng hợp tác"

    def to_table_row(self):
        """Tuple hiển thị trên Treeview."""
        return (
            self.ma_ncc,
            self.ten_ncc,
            self.nguoi_lh or "—",
            self.so_dt    or "—",
            self.email    or "—",
            self.trang_thai_str,
        )

    @staticmethod
    def from_row(row):
        """
        Tạo Supplier từ dòng query.
        row = (ma_ncc, ten_ncc, nguoi_lh, dia_chi, so_dt,
               email, website, ghi_chu, trang_thai)
        """
        return Supplier(
            ma_ncc   = row[0],
            ten_ncc  = row[1] or "",
            nguoi_lh = row[2] or "",
            dia_chi  = row[3] or "",
            so_dt    = row[4] or "",
            email    = row[5] or "",
            website  = row[6] or "" if len(row) > 6 else "",
            ghi_chu  = row[7] or "" if len(row) > 7 else "",
            trang_thai = row[8] if len(row) > 8 else 1,
        )

    def __str__(self):
        return f"[NCC#{self.ma_ncc}] {self.ten_ncc} | {self.so_dt}"