# backend/controllers/stock_controller.py
# ================================================================
# StockController — điều phối StockFrame ↔ StockService
# ================================================================

from backend.modules.stock_service    import StockService
from backend.modules.supplier_service import SupplierService
from backend.modules.product_service  import ProductService
from backend.models.stock_entry import StockEntry


class StockController:
    def __init__(self):
        self._svc     = StockService()
        self._ncc_svc = SupplierService()
        self._sp_svc  = ProductService()

    def get_products(self, keyword: str = ""):
        return self._sp_svc.search(keyword) if keyword else self._sp_svc.get_all()

    def get_suppliers(self) -> list:
        """Danh sách NCC đang hoạt động cho Combobox."""
        return self._ncc_svc.get_dropdown()

    def save_entry(self, entry: StockEntry) -> dict:
        """Lưu phiếu nhập và cập nhật tồn kho."""
        ok, result = self._svc.create_entry(entry)
        if ok:
            return {"ok": True, "ma_phieu": result, "msg": "Lưu phiếu nhập thành công!"}
        return {"ok": False, "ma_phieu": None, "msg": str(result)}

    def get_entries(self, tu_ngay=None, den_ngay=None) -> list:
        return self._svc.get_entries(tu_ngay, den_ngay)

    def get_entry_detail(self, ma_phieu: int) -> list:
        return self._svc.get_entry_detail(ma_phieu)