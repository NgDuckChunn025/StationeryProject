# backend/controllers/supplier_controller.py
# ================================================================
# SupplierController — điều phối SupplierFrame ↔ SupplierService
# ================================================================

from backend.modules.supplier_service import SupplierService
from backend.models.supplier import Supplier


class SupplierController:
    def __init__(self):
        self._svc = SupplierService()

    def load_list(self, keyword: str = "",
                  chi_hoat_dong: bool = False) -> list[Supplier]:
        return self._svc.get_all(keyword, chi_hoat_dong)

    def get_detail(self, ma_ncc: int) -> Supplier | None:
        return self._svc.get_by_id(ma_ncc)

    def save(self, ma_ncc, ten_ncc: str, nguoi_lh: str, so_dt: str,
             email: str, dia_chi: str, website: str) -> dict:
        s = Supplier(
            ma_ncc=ma_ncc, ten_ncc=ten_ncc, nguoi_lh=nguoi_lh,
            so_dt=so_dt, email=email, dia_chi=dia_chi, website=website,
        )
        ok, msg = self._svc.update(s) if ma_ncc else self._svc.add(s)
        return {"ok": ok, "msg": msg}

    def toggle_status(self, ma_ncc: int) -> dict:
        ok, msg = self._svc.toggle_status(ma_ncc)
        return {"ok": ok, "msg": msg}