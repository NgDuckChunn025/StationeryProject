# backend/controllers/category_controller.py
# ================================================================
# CategoryController — điều phối View ↔ CategoryService
# ================================================================

from backend.modules.category_service import CategoryService
from backend.models.product_category  import ProductCategory


class CategoryController:
    def __init__(self):
        self._svc = CategoryService()

    def load_list(self, keyword: str = "") -> list[ProductCategory]:
        return self._svc.get_all(keyword)

    def get_detail(self, ma_loai: int) -> ProductCategory | None:
        return self._svc.get_by_id(ma_loai)

    def save(self, ma_loai, ten_loai: str, mo_ta: str = "") -> dict:
        cat = ProductCategory(ma_loai=ma_loai, ten_loai=ten_loai, mo_ta=mo_ta)
        ok, msg = self._svc.update(cat) if ma_loai else self._svc.add(cat)
        return {"ok": ok, "msg": msg}

    def remove(self, ma_loai: int) -> dict:
        ok, msg = self._svc.delete(ma_loai)
        return {"ok": ok, "msg": msg}

    def get_dropdown(self) -> list[dict]:
        return self._svc.get_dropdown()

    def count_products(self, ma_loai: int) -> int:
        return self._svc.count_products(ma_loai)