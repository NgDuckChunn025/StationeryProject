# backend/controllers/__init__.py
from backend.controllers.customer_controller  import CustomerController
from backend.controllers.product_controller   import ProductController
from backend.controllers.sales_controller     import SalesController
from backend.controllers.stock_controller     import StockController
from backend.controllers.staff_controller     import StaffController
from backend.controllers.supplier_controller  import SupplierController


__all__ = [
    "CustomerController", "ProductController",
    "SalesController",    "StockController",
    "StaffController",    "SupplierController",
]