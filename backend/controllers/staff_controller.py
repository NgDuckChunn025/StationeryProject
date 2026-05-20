# backend/controllers/staff_controller.py
# ================================================================
# StaffController — điều phối StaffFrame ↔ StaffService
# ================================================================

from backend.modules.staff_service import StaffService
from backend.models.staff import Staff


class StaffController:
    def __init__(self, ma_nv_hien_tai: int):
        """ma_nv_hien_tai: mã NV đang đăng nhập (để bảo vệ toggle_status)."""
        self._svc               = StaffService()
        self._ma_nv_hien_tai    = ma_nv_hien_tai

    def load_list(self, keyword: str = "") -> list[Staff]:
        return self._svc.get_all(keyword)

    def get_detail(self, ma_nv: int) -> Staff | None:
        return self._svc.get_by_id(ma_nv)

    def add(self, ten: str, tai_khoan: str, mat_khau: str,
            vai_tro: str, so_dt: str = "") -> dict:
        ok, msg = self._svc.add(ten, tai_khoan, mat_khau, vai_tro, so_dt)
        return {"ok": ok, "msg": msg}

    def update(self, e: Staff) -> dict:
        ok, msg = self._svc.update(e)
        return {"ok": ok, "msg": msg}

    def reset_password(self, ma_nv: int, mat_khau_moi: str) -> dict:
        ok, msg = self._svc.reset_password(ma_nv, mat_khau_moi)
        return {"ok": ok, "msg": msg}

    def toggle_status(self, ma_nv: int) -> dict:
        ok, msg = self._svc.toggle_status(ma_nv, self._ma_nv_hien_tai)
        return {"ok": ok, "msg": msg}

    def remove(self, ma_nv: int) -> dict:
        ok, msg = self._svc.delete(ma_nv)
        return {"ok": ok, "msg": msg}