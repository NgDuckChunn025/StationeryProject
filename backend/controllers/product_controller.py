# backend/controllers/product_controller.py
# ================================================================
# ProductController — điều phối ProductFrame ↔ ProductService
# ================================================================

from backend.modules.product_service  import ProductService
from backend.modules.category_service import CategoryService
from backend.models.product import Product


class ProductController:
    def __init__(self):
        self._svc     = ProductService()
        self._cat_svc = CategoryService()

    def load_list(self, keyword: str = "") -> list[Product]:
        """Tải danh sách sản phẩm (tìm kiếm hoặc tất cả)."""
        return self._svc.search(keyword) if keyword else self._svc.get_all()

    def get_detail(self, ma_sp: int) -> Product | None:
        return self._svc.get_by_id(ma_sp)

    def get_categories(self) -> list[dict]:
        """Trả danh mục để đổ vào Combobox của ProductDialog."""
        return self._cat_svc.get_dropdown()

    def save(self, ma_sp, ma_code: str, ten_sp: str, ma_loai,
             don_vi: str, gia_nhap: float, gia_ban: float,
             ton_kho: int, mo_ta: str = "") -> dict:
        p = Product(
            ma_sp=ma_sp, ma_code=ma_code, ten_sp=ten_sp,
            ma_loai=ma_loai, don_vi=don_vi,
            gia_nhap=gia_nhap, gia_ban=gia_ban,
            ton_kho=ton_kho, mo_ta=mo_ta,
        )
        ok, msg = self._svc.update(p) if ma_sp else self._svc.add(p)
        return {"ok": ok, "msg": msg}

    def remove(self, ma_sp: int) -> dict:
        """Ẩn sản phẩm (soft-delete)."""
        ok, msg = self._svc.delete(ma_sp)
        return {"ok": ok, "msg": msg}

    def get_low_stock(self, threshold: int = 10) -> list[Product]:
        return self._svc.get_low_stock(threshold)