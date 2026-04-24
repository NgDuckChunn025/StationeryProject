# Mô tả các lớp (Class) — VPP Manager
> **Dự án:** Quản lý Cửa hàng Văn phòng phẩm  
> **Ngôn ngữ:** Python 3.12 · CustomTkinter · MySQL 8  
> **Kiến trúc:** 4 tầng — View → Controller → Service → Model  
> **Tổng số class:** 34 (11 View · 7 Controller · 8 Service · 9 Model)

---

## Tổng quan kiến trúc 4 tầng

```
┌─────────────────────────────────────────────────┐
│  TẦNG VIEW  (frontend/gui/)                     │
│  Hiển thị giao diện, nhận thao tác người dùng  │
└───────────────────┬─────────────────────────────┘
                    │ gọi controller
┌───────────────────▼─────────────────────────────┐
│  TẦNG CONTROLLER  (backend/controllers/)         │
│  Điều phối: nhận sự kiện → gọi Service → trả   │
│  kết quả {"ok": bool, "msg": str} về View       │
└───────────────────┬─────────────────────────────┘
                    │ gọi service
┌───────────────────▼─────────────────────────────┐
│  TẦNG SERVICE  (backend/modules/)               │
│  Xử lý nghiệp vụ, truy vấn DB, trả Model       │
└───────────────────┬─────────────────────────────┘
                    │ dùng model
┌───────────────────▼─────────────────────────────┐
│  TẦNG MODEL  (backend/models/)                  │
│  Đối tượng nghiệp vụ, ánh xạ dữ liệu từ DB     │
└─────────────────────────────────────────────────┘
```

**Nguyên tắc thiết kế:**
- Mỗi tầng chỉ biết tầng ngay bên dưới — View không gọi Service trực tiếp
- Mỗi class có một trách nhiệm duy nhất (Single Responsibility Principle)
- Service giữ hàm module-level làm alias → UI cũ không cần sửa khi refactor

---

# TẦNG VIEW — `frontend/gui/`

> **Nhiệm vụ tổng thể:** Hiển thị giao diện đồ họa bằng CustomTkinter, nhận thao tác từ người dùng (click, nhập liệu), gọi Controller và hiển thị kết quả. Tầng này **không chứa logic nghiệp vụ**, **không truy vấn DB trực tiếp**.

---

## 1. LoginWindow
**File:** `frontend/gui/login_ui.py` | **Kế thừa:** `CTkToplevel`

**Ý nghĩa:** Cửa sổ đăng nhập — màn hình đầu tiên khi khởi động ứng dụng.

**Nhiệm vụ:**
- Hiển thị form nhập tài khoản và mật khẩu
- Gọi `auth_service.login()` để xác thực
- Nếu đúng: lưu thông tin user vào `self.user_info`, đóng cửa sổ để `main.py` mở `MainWindow`
- Nếu sai: hiển thị thông báo lỗi màu đỏ ngay bên dưới form

| Thuộc tính | Mô tả |
|------------|-------|
| `user_info` | Dict user sau khi đăng nhập thành công |
| `ent_tk` | Ô nhập tài khoản |
| `ent_mk` | Ô nhập mật khẩu (ẩn ký tự •••) |

| Phương thức | Mô tả |
|-------------|-------|
| `_do_login()` | Lấy giá trị form, gọi service, xử lý kết quả |
| `_show_error(msg)` | Hiển thị label lỗi màu đỏ |

---

## 2. MainWindow
**File:** `frontend/gui/main_window.py` | **Kế thừa:** `CTk`

**Ý nghĩa:** Cửa sổ chính của ứng dụng — khung chứa sidebar menu và vùng nội dung trung tâm.

**Nhiệm vụ:**
- Xây dựng sidebar với các mục menu tương ứng vai trò (admin thấy thêm Nhân viên, Nhà cung cấp)
- Điều hướng giữa các màn hình khi người dùng click menu
- Quản lý vùng nội dung trung tâm (xóa frame cũ, tạo frame mới)
- Xử lý Đăng xuất

| Thuộc tính | Mô tả |
|------------|-------|
| `user` | Dict thông tin nhân viên đang đăng nhập |
| `content` | Frame vùng nội dung trung tâm |

| Phương thức | Mô tả |
|-------------|-------|
| `_navigate(key)` | Xóa nội dung cũ, tạo Frame mới tương ứng key |
| `_build_sidebar()` | Tạo nút menu dựa theo `user["vai_tro"]` |
| `_logout()` | Đóng MainWindow, mở lại LoginWindow |

---

## 3. DashboardFrame
**File:** `frontend/gui/dashboard_ui.py` | **Kế thừa:** `CTkFrame`

**Ý nghĩa:** Trang chủ sau khi đăng nhập — tổng quan toàn bộ hoạt động cửa hàng.

**Nhiệm vụ:**
- Hiển thị 4 thẻ thống kê: Doanh thu hôm nay, Số hóa đơn, Sản phẩm sắp hết, Khách hàng mới
- Biểu đồ doanh thu 7 ngày gần nhất
- Danh sách sản phẩm tồn kho thấp (cảnh báo đỏ)
- 5 hóa đơn gần nhất

---

## 4. CustomerFrame + CustomerDialog
**File:** `frontend/gui/customer_ui.py`

### CustomerFrame (màn hình danh sách)
**Ý nghĩa:** Quản lý khách hàng — xem, tìm kiếm, thêm, sửa, xóa.

**Nhiệm vụ:**
- Treeview danh sách với cột: Mã KH, Họ tên, SĐT, Địa chỉ, Hạng, Điểm tích lũy
- Tìm kiếm real-time (lọc ngay khi gõ phím)
- Các nút Thêm/Sửa/Xóa gọi `CustomerController`

| Thuộc tính | Mô tả |
|------------|-------|
| `ctrl` | Instance của `CustomerController` |
| `tree` | Treeview hiển thị danh sách |
| `ent_search` | Ô tìm kiếm |

### CustomerDialog (hộp thoại thêm/sửa)
**Ý nghĩa:** Form nhập thông tin khách hàng.

**Nhiệm vụ:**
- `customer=None` → form trống (thêm mới)
- `customer` có giá trị → điền sẵn thông tin cũ qua `_fill()` (chỉnh sửa)
- Gọi `CustomerController.save()` khi nhấn Lưu, callback `_load()` để refresh danh sách

---

## 5. ProductFrame + ProductDialog
**File:** `frontend/gui/product_ui.py`

### ProductFrame
**Ý nghĩa:** Quản lý sản phẩm — xem, tìm kiếm, thêm, sửa, ẩn.

**Nhiệm vụ:**
- Treeview: Mã, Tên, Loại, ĐVT, Giá nhập, Giá bán, Tồn kho
- Tô nền đỏ nhạt các hàng có tồn kho ≤ 10
- Tìm kiếm theo tên và mã code

### ProductDialog
**Nhiệm vụ:**
- Combobox Loại SP đọc từ `ProductController.get_categories()`
- Tự tính và hiển thị % lợi nhuận khi thay đổi giá nhập/bán

---

## 6. SalesFrame
**File:** `frontend/gui/sales_ui.py` | **Kế thừa:** `CTkFrame`

**Ý nghĩa:** Màn hình bán hàng — giao diện POS (Point of Sale) chính.

**Nhiệm vụ:**
- Chia 2 cột: trái = tìm/chọn sản phẩm, phải = danh sách hóa đơn đang soạn
- Thêm sản phẩm vào hóa đơn (`invoice.add_item()` — cộng dồn nếu trùng mã)
- Chọn khách hàng, nhập giảm giá, chọn hình thức thanh toán
- Thanh toán → `SalesController.checkout()` → trừ tồn kho + cộng điểm KH + lưu DB

| Thuộc tính | Mô tả |
|------------|-------|
| `ctrl` | Instance của `SalesController` |
| `invoice` | Đối tượng `Invoice` đang soạn (in-memory) |

---

## 7. StockFrame
**File:** `frontend/gui/stock_ui.py` | **Kế thừa:** `CTkFrame`

**Ý nghĩa:** Màn hình nhập kho — tạo phiếu nhập hàng từ nhà cung cấp.

**Nhiệm vụ:**
- Chọn NCC từ Combobox (lấy từ `StockController.get_suppliers()`)
- Tìm và thêm sản phẩm vào phiếu
- Lưu phiếu → `StockController.save_entry()` → cộng tồn kho + lưu DB

---

## 8. StaffFrame
**File:** `frontend/gui/staff_ui.py` | **Chỉ admin**

**Ý nghĩa:** Quản lý tài khoản nhân viên — thêm, xem, khóa/mở.

**Nhiệm vụ:**
- Treeview: Mã NV, Họ tên, Tài khoản, Vai trò, SĐT, Trạng thái
- Thêm nhân viên mới (tự động hash mật khẩu)
- **Khóa/Mở tài khoản** thay vì Xóa (dùng `toggle_status`) — bảo toàn lịch sử hóa đơn
- Đặt lại mật khẩu

---

## 9. SupplierFrame + SupplierDialog
**File:** `frontend/gui/supplier_ui.py` | **Chỉ admin**

**Ý nghĩa:** Quản lý nhà cung cấp — thêm, sửa, đổi trạng thái hợp tác.

**Nhiệm vụ:**
- Treeview: Mã NCC, Tên, Người LH, SĐT, Email, Trạng thái
- Checkbox lọc chỉ NCC đang hoạt động
- Không xóa NCC — chỉ Ngừng/Tiếp tục hợp tác (vì có phiếu nhập liên kết)

---

# TẦNG CONTROLLER — `backend/controllers/`

> **Nhiệm vụ tổng thể:** Cầu nối giữa View và Service. Nhận dữ liệu thô từ form (chuỗi text), tạo đối tượng Model, gọi Service, trả về `dict {"ok": bool, "msg": str}`. **Không biết gì về Tkinter, không truy vấn DB.**

---

## 10. CustomerController
**File:** `backend/controllers/customer_controller.py`

**Ý nghĩa:** Điều phối toàn bộ nghiệp vụ khách hàng.

| Phương thức | Nhiệm vụ |
|-------------|---------|
| `load_list(keyword)` | Lấy danh sách KH để đổ vào Treeview |
| `get_detail(ma_kh)` | Lấy 1 KH để điền vào form sửa |
| `save(ma_kh, ten, so_dt, dia_chi, email)` | Tạo object Customer → gọi `add()` hoặc `update()` |
| `remove(ma_kh)` | Kiểm tra điều kiện, gọi `delete()` |
| `add_points(ma_kh, so_tien)` | Cộng điểm sau thanh toán (được gọi từ SalesController) |

---

## 11. ProductController
**File:** `backend/controllers/product_controller.py`

**Ý nghĩa:** Điều phối nghiệp vụ sản phẩm, tích hợp CategoryService.

**Đặc biệt:** Dùng **2 Service**: `ProductService` (CRUD SP) và `CategoryService` (lấy danh mục cho Combobox). Ví dụ điển hình Controller tổng hợp nhiều nguồn dữ liệu.

---

## 12. SalesController
**File:** `backend/controllers/sales_controller.py`

**Ý nghĩa:** Điều phối bán hàng — Controller phức tạp nhất.

**Đặc biệt:** Dùng **3 Service**: `SalesService` + `CustomerService` + `ProductService`.

**Luồng `checkout(invoice)`:**
1. `SalesService.create_invoice()` → lưu DB trong transaction, trừ tồn kho
2. Nếu thành công và có `ma_kh` → `CustomerService.add_points()`
3. Trả `{"ok": True, "ma_hd": ..., "msg": "Thanh toán thành công!"}`

---

## 13. StockController
**File:** `backend/controllers/stock_controller.py`

**Ý nghĩa:** Điều phối nhập kho.

**Đặc biệt:** Gọi `SupplierService.get_dropdown()` thay vì hàm `add_supplier()` trùng cũ đã bị xóa — Controller biết lấy NCC từ đúng service.

---

## 14. StaffController
**File:** `backend/controllers/staff_controller.py`

**Ý nghĩa:** Điều phối quản lý nhân viên.

**Đặc biệt:** Constructor nhận `ma_nv_hien_tai` để bảo vệ — không cho admin tự khóa tài khoản đang dùng.

---

## 15. SupplierController
**File:** `backend/controllers/supplier_controller.py`

**Ý nghĩa:** Điều phối quản lý nhà cung cấp — thêm, sửa, đổi trạng thái.

---

## 16. CategoryController
**File:** `backend/controllers/category_controller.py`

**Ý nghĩa:** Điều phối quản lý danh mục sản phẩm *(mới bổ sung)*.

**Đặc biệt:** `count_products(ma_loai)` — đếm SP thuộc loại trước khi cho phép xóa.

---

# TẦNG SERVICE — `backend/modules/`

> **Nhiệm vụ tổng thể:** Chứa toàn bộ **logic nghiệp vụ** và **truy vấn SQL**. Giao tiếp với MySQL qua `get_connection()`, tạo đối tượng Model từ kết quả query. Mỗi class có singleton instance + hàm module-level làm alias để tương thích ngược với code cũ.

---

## 17. AuthService
**File:** `backend/modules/auth_service.py`

**Ý nghĩa:** Xác thực danh tính và phân quyền.

| Phương thức | Nhiệm vụ |
|-------------|---------|
| `login(tai_khoan, mat_khau)` | Query DB, so sánh bcrypt hash, trả dict user hoặc None |
| `is_admin(nv)` | Kiểm tra `vai_tro == "admin"` |
| `hash_password(mk)` | Tạo bcrypt hash để lưu DB |
| `change_password(id, cu, moi)` | Xác minh mật khẩu cũ trước khi đổi |

**Bảo mật:** Dùng `bcrypt.checkpw()` — không bao giờ so sánh plain text.

---

## 18. CustomerService
**File:** `backend/modules/customer_service.py`

**Ý nghĩa:** CRUD khách hàng và nghiệp vụ tích điểm.

| Phương thức | Nhiệm vụ |
|-------------|---------|
| `get_all(keyword)` | SELECT với LIKE nếu có keyword |
| `get_by_id(ma_kh)` | SELECT 1 bản ghi |
| `add(c)` | INSERT sau khi `c.validate()` |
| `update(c)` | UPDATE theo `ma_kh` |
| `delete(ma_kh)` | Kiểm tra không có hóa đơn rồi DELETE |
| `add_points(ma_kh, so_tien)` | `diem += int(so_tien // 10_000)` |

---

## 19. ProductService
**File:** `backend/modules/product_service.py`

**Ý nghĩa:** CRUD sản phẩm, tìm kiếm, cảnh báo tồn kho.

**Đặc biệt:**
- `delete()` là **soft delete** — chỉ set `trang_thai=0`, giữ lịch sử hóa đơn
- `get_low_stock(threshold)` — lấy SP có `ton_kho <= threshold` cho Dashboard

---

## 20. SalesService
**File:** `backend/modules/sales_service.py`

**Ý nghĩa:** Lưu hóa đơn và quản lý lịch sử bán hàng.

**`create_invoice(invoice)` — quan trọng nhất:**
- Chạy trong **transaction** duy nhất (INSERT hóa đơn + INSERT chi tiết + UPDATE tồn kho)
- Nếu UPDATE `ton_kho` trả `rowcount=0` → raise Exception "không đủ hàng"
- Nếu có lỗi → `rollback()` — không mất dữ liệu

---

## 21. StockService
**File:** `backend/modules/stock_service.py`

**Ý nghĩa:** Tạo phiếu nhập và cập nhật tồn kho.

**`create_entry(entry)`** — đối xứng với `create_invoice()`:
- Transaction: INSERT phiếu nhập + INSERT chi tiết + UPDATE `ton_kho += so_luong`

**Thay đổi:** Đã xóa `add_supplier()` trùng với `SupplierService`.

---

## 22. StaffService
**File:** `backend/modules/staff_service.py`

**Ý nghĩa:** CRUD nhân viên đầy đủ *(bổ sung `update`, `reset_password`, `toggle_status`)*.

| Phương thức | Mô tả |
|-------------|-------|
| `get_all(keyword)` | Tìm theo tên/tài khoản |
| `get_by_id(ma_nv)` | Lấy 1 NV để sửa |
| `add(ten, tk, mk, role, so_dt)` | Kiểm tra tài khoản trùng, hash mật khẩu, INSERT |
| `update(e)` | Cập nhật tên/tài khoản/vai trò/SĐT |
| `reset_password(id, mk)` | Admin đặt lại mật khẩu |
| `toggle_status(id, id_hientai)` | Khóa/Mở — từ chối nếu `id == id_hientai` |
| `delete(ma_nv)` | Kiểm tra không có hóa đơn rồi DELETE |

---

## 23. SupplierService
**File:** `backend/modules/supplier_service.py`

**Ý nghĩa:** CRUD nhà cung cấp.

**`get_dropdown()`** — trả `[(ma_ncc, ten_ncc)]` chỉ NCC đang hoạt động, dùng cho Combobox nhập kho.

---

## 24. CategoryService
**File:** `backend/modules/category_service.py` *(mới)*

**Ý nghĩa:** CRUD danh mục sản phẩm — bổ sung sau khi phát hiện `ProductCategory` có model nhưng thiếu service.

**`count_products(ma_loai)`** — đếm SP thuộc loại; nếu > 0 → từ chối xóa loại.

---

# TẦNG MODEL — `backend/models/`

> **Nhiệm vụ tổng thể:** Đại diện các thực thể nghiệp vụ. Ánh xạ với bảng DB, validate dữ liệu, chuyển đổi giữa DB và giao diện. Tất cả tuân theo **pattern 4 method**: `validate()`, `from_row()`, `to_table_row()`, `__str__()`.

---

## 25. Customer — Khách hàng
**Bảng DB:** `khach_hang`

**Ý nghĩa:** Đại diện khách hàng đăng ký — có thể tích điểm và phân hạng (Thường/Bạc/Vàng/Bạch Kim).

| Thuộc tính | Kiểu | Mô tả |
|------------|------|-------|
| `ma_kh` | `int\|None` | PK (None = chưa lưu DB) |
| `ten_kh` | `str` | Họ tên *(bắt buộc)* |
| `so_dt` | `str` | Chỉ chứa chữ số |
| `dia_chi` | `str` | Địa chỉ |
| `email` | `str` | Email |
| `diem_tich_luy` | `int` | Tự động cộng khi mua hàng |

**Validate:** tên không trống, SĐT chỉ chứa chữ số.

---

## 26. Employee — Nhân viên
**Bảng DB:** `nhan_vien`

**Ý nghĩa:** Tài khoản người dùng hệ thống với 2 vai trò: `admin` và `nhanvien`.

**Property computed:**
- `trang_thai_str` → `"Hoạt động"` / `"Tạm khóa"`
- `vai_tro_str` → `"Quản trị"` / `"Nhân viên"`

**Bảo mật:** `mat_khau` luôn là bcrypt hash.

---

## 27. Supplier — Nhà cung cấp *(mới)*
**Bảng DB:** `nha_cung_cap`

**Ý nghĩa:** Đối tác cung cấp hàng hóa. Không xóa cứng — chỉ đổi `trang_thai`.

**Property:** `trang_thai_str` → `"Hoạt động"` / `"Ngừng hợp tác"`

---

## 28. ProductCategory — Loại sản phẩm
**Bảng DB:** `loai_san_pham`

**Ý nghĩa:** Nhóm phân loại sản phẩm (Bút, Vở, Giấy, Dụng cụ...). 1 loại → nhiều sản phẩm.

---

## 29. Product — Sản phẩm
**Bảng DB:** `san_pham` (JOIN `loai_san_pham`)

**Ý nghĩa:** Hàng hóa kinh doanh — thực thể trung tâm.

**Property computed (không lưu DB):**

| Property | Công thức | Mô tả |
|----------|-----------|-------|
| `loi_nhuan` | `gia_ban - gia_nhap` | Lợi nhuận/đơn vị |
| `ty_le_loi_nhuan` | `(loi_nhuan / gia_nhap) × 100` | % lợi nhuận |
| `sap_het` | `ton_kho <= 10` | Cảnh báo tồn thấp |

**Soft delete:** `trang_thai=0` thay vì DELETE — giữ lịch sử hóa đơn.

---

## 30 & 31. Invoice + InvoiceItem — Hóa đơn bán hàng
**Bảng DB:** `hoa_don` + `chi_tiet_hoa_don`

**Ý nghĩa:** Hóa đơn đang soạn trong bộ nhớ tại màn hình POS.  
**Quan hệ Composition:** `Invoice ◆──► InvoiceItem`

**Invoice — Property computed:**
- `tong_tien = Σ(item.thanh_tien)` — tính realtime
- `thanh_toan = max(0, tong_tien - giam_gia)`
- `so_mon = len(items)`

**`add_item()`** — nếu SP đã có → cộng dồn số lượng, không tạo dòng mới.

**InvoiceItem:** `don_gia` chốt tại thời điểm bán — không đổi kể cả sau này giá SP thay đổi.

---

## 32 & 33. StockEntry + StockItem — Phiếu nhập kho
**Bảng DB:** `phieu_nhap` + `chi_tiet_phieu_nhap`

**Ý nghĩa:** Phiếu nhập đang soạn trong bộ nhớ. Cấu trúc **đối xứng** với Invoice.  
**Quan hệ Composition:** `StockEntry ◆──► StockItem`

| So sánh | Invoice | StockEntry |
|---------|---------|-----------|
| Đối tác | Customer (mua từ ta) | Supplier (ta mua từ họ) |
| Tồn kho | Giảm | Tăng |
| Giảm giá | Có | Không |
| Hạn sử dụng | Không | Có (`han_su_dung`) |

---

## Sơ đồ quan hệ tổng hợp

```
ProductCategory ◄──── Product
                          │
Customer ──┐              │
           ▼              ▼
Employee──►Invoice ◆──► InvoiceItem ──► Product

Supplier ──┐
           ▼
Employee──►StockEntry ◆──► StockItem ──► Product
```

| Ký hiệu | Ý nghĩa |
|---------|---------|
| `◆──►` | Composition — con không tồn tại khi cha bị xóa |
| `──►` | Association — tham chiếu qua FK |