# backend/models/product_category.py
# ================================================================
# Model ProductCategory — đại diện loại sản phẩm
# ================================================================

from typing import Optional, Tuple


class ProductCategory:
    def __init__(
        self,
        ma_loai: Optional[int] = None,
        ten_loai: str = "",
        mo_ta: str = ""
    ):
        self.ma_loai = ma_loai
        self.ten_loai = ten_loai.strip()
        self.mo_ta = mo_ta.strip() if mo_ta else ""

    # ============================================================
    # VALIDATION
    # ============================================================
    def validate(self) -> Tuple[bool, str]:
        """
        Kiểm tra dữ liệu hợp lệ trước khi thêm/sửa.
        """
        if not self.ten_loai:
            return False, "Tên loại không được để trống!"
        if len(self.ten_loai) < 2:
            return False, "Tên loại phải có ít nhất 2 ký tự!"
        if len(self.ten_loai) > 100:
            return False, "Tên loại không được quá 100 ký tự!"
        return True, ""

    # ============================================================
    # MAPPING DB → OBJECT
    # ============================================================
    @staticmethod
    def from_row(row) -> "ProductCategory":
        """
        Tạo object từ dữ liệu DB (tuple).
        """
        if not row:
            return None
        return ProductCategory(
            ma_loai=row[0],
            ten_loai=row[1],
            mo_ta=row[2] if len(row) > 2 else ""
        )

    # ============================================================
    # OBJECT → DICT
    # ============================================================
    def to_dict(self) -> dict:
        return {
            "ma_loai": self.ma_loai,
            "ten_loai": self.ten_loai,
            "mo_ta": self.mo_ta
        }

    # ============================================================
    # HIỂN THỊ TABLE (GUI)
    # ============================================================
    def to_table_row(self) -> tuple:
        """
        Dùng cho Treeview (nếu cần).
        """
        return (
            self.ma_loai,
            self.ten_loai,
            self.mo_ta or "—"
        )

    # ============================================================
    # DEBUG
    # ============================================================
    def __repr__(self) -> str:
        return (
            f"ProductCategory("
            f"ma_loai={self.ma_loai}, "
            f"ten_loai='{self.ten_loai}', "
            f"mo_ta='{self.mo_ta}')"
        )