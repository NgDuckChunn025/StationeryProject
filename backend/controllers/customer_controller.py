# backend/controllers/customer_controller.py
# ================================================================
# CustomerController — nhận sự kiện từ View, gọi Service,
#                      trả kết quả về View (không biết Tkinter)
# ================================================================

from backend.modules.customer_service import CustomerService
from backend.models.customer import Customer


class CustomerController:
    """
    Tầng điều phối giữa CustomerFrame (View) và CustomerService.
    View gọi controller — controller gọi service — trả dict kết quả.
    """

    def __init__(self):
        self._svc = CustomerService()

    # ── Truy vấn ─────────────────────────────────────────────
    def load_list(self, keyword: str = "") -> list[Customer]:
        """Tải danh sách khách hàng cho Treeview."""
        return self._svc.get_all(keyword)

    def get_detail(self, ma_kh: int) -> Customer | None:
        """Tải thông tin một khách hàng để điền vào Dialog."""
        return self._svc.get_by_id(ma_kh)

    # ── Nghiệp vụ ────────────────────────────────────────────
    def save(self, ma_kh, ten_kh: str, so_dt: str,
             dia_chi: str, email: str) -> dict:
        """
        Tạo hoặc cập nhật khách hàng.
        Trả {'ok': bool, 'msg': str}.
        """
        c = Customer(
            ma_kh=ma_kh, ten_kh=ten_kh,
            so_dt=so_dt, dia_chi=dia_chi, email=email,
        )
        ok, msg = self._svc.update(c) if ma_kh else self._svc.add(c)
        return {"ok": ok, "msg": msg}

    def remove(self, ma_kh: int) -> dict:
        """Xóa khách hàng nếu chưa có hóa đơn."""
        ok, msg = self._svc.delete(ma_kh)
        return {"ok": ok, "msg": msg}

    def add_points(self, ma_kh: int, so_tien: float) -> None:
        """Cộng điểm sau khi bán hàng (gọi từ SalesController)."""
        self._svc.add_points(ma_kh, so_tien)