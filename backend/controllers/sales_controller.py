# backend/controllers/sales_controller.py
# ================================================================
# SalesController — điều phối SalesFrame ↔ SalesService
# ================================================================

from backend.modules.sales_service    import SalesService
from backend.modules.customer_service import CustomerService
from backend.modules.product_service  import ProductService
from backend.models.invoice import Invoice


class SalesController:
    def __init__(self):
        self._svc     = SalesService()
        self._kh_svc  = CustomerService()
        self._sp_svc  = ProductService()

    def get_products(self, keyword: str = ""):
        """Tìm sản phẩm để thêm vào hóa đơn."""
        return self._sp_svc.search(keyword) if keyword else self._sp_svc.get_all()

    def get_customers(self) -> list:
        """Danh sách khách hàng cho Combobox."""
        return self._svc.get_customers()

    def checkout(self, invoice: Invoice) -> dict:
        """
        Thanh toán hóa đơn: lưu DB + cộng điểm khách hàng.
        Trả {'ok': bool, 'ma_hd': int | None, 'msg': str}.
        """
        ok, result = self._svc.create_invoice(invoice)
        if ok:
            if invoice.ma_kh:
                self._kh_svc.add_points(invoice.ma_kh, invoice.thanh_toan)
            return {"ok": True, "ma_hd": result, "msg": "Thanh toán thành công!"}
        return {"ok": False, "ma_hd": None, "msg": str(result)}

    def get_invoices(self, tu_ngay=None, den_ngay=None) -> list:
        return self._svc.get_invoices(tu_ngay, den_ngay)

    def get_invoice_detail(self, ma_hd: int) -> list:
        return self._svc.get_invoice_detail(ma_hd)