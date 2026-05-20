# backend/models/__init__.py
from backend.models.product     import Product
from backend.models.invoice     import Invoice, InvoiceItem
from backend.models.customer    import Customer
from backend.models.staff    import Staff
from backend.models.stock_entry import StockEntry, StockItem
from backend.models.supplier    import Supplier          # mới thêm

__all__ = [
    "Product", "Invoice", "InvoiceItem",
    "Customer", "Staff",
    "StockEntry", "StockItem",
    "Supplier",
]


