# backend/models/employee.py
# ================================================================
# Class Employee (NhanVien) — đối tượng nghiệp vụ nhân viên
# ================================================================


class Staff:
    VAI_TRO_CHOICES = ["admin", "nhanvien"]

    def __init__(self, ma_nv=None, ten_nv="", tai_khoan="",
                 mat_khau="", vai_tro="nhanvien", so_dt="", trang_thai=1):
        self.ma_nv      = ma_nv
        self.ten_nv     = ten_nv.strip()     if ten_nv     else ""
        self.tai_khoan  = tai_khoan.strip()  if tai_khoan  else ""
        self.mat_khau   = mat_khau           # already hashed or plain
        self.vai_tro    = vai_tro if vai_tro in self.VAI_TRO_CHOICES else "nhanvien"
        self.so_dt      = so_dt.strip()      if so_dt      else ""
        self.trang_thai = int(trang_thai)

    # ---- Validation ----
    def validate(self) -> tuple[bool, str]:
        if not self.ten_nv:
            return False, "Tên nhân viên không được trống!"
        if not self.tai_khoan:
            return False, "Tài khoản không được trống!"
        if len(self.tai_khoan) < 4:
            return False, "Tài khoản phải có ít nhất 4 ký tự!"
        return True, ""

    # ---- Display ----
    @property
    def trang_thai_str(self):
        return "Hoạt động" if self.trang_thai else "Tạm khóa"

    @property
    def vai_tro_str(self):
        return "Quản trị" if self.vai_tro == "admin" else "Nhân viên"

    def to_table_row(self):
        """Tuple hiển thị trên Treeview."""
        return (
            self.ma_nv,
            self.ten_nv,
            self.tai_khoan,
            self.vai_tro_str,
            self.so_dt or "—",
            self.trang_thai_str,
        )

    @staticmethod
    def from_row(row):
        """
        Tạo Employee từ dòng query.
        row = (ma_nv, ten_nv, tai_khoan, vai_tro, so_dt, trang_thai)
        """
        return Staff(
            ma_nv      = row[0],
            ten_nv     = row[1] or "",
            tai_khoan  = row[2] or "",
            vai_tro    = row[3] or "nhanvien",
            so_dt      = row[4] or "",
            trang_thai = row[5] if len(row) > 5 else 1,
        )

    def __str__(self):
        return f"[NV#{self.ma_nv}] {self.ten_nv} ({self.tai_khoan}) — {self.vai_tro_str}"