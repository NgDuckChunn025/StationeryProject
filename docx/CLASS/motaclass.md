# Mô tả các lớp (Class) — VPP Manager

> **Dự án:** Quản lý Cửa hàng Văn phòng phẩm  
> **Ngôn ngữ:** Python 3.12  
> **Thư mục:** `backend/models/`  
> **Tổng số lớp:** 8 (6 model chính + 2 lớp chi tiết dạng Composition)

---

## Tổng quan kiến trúc lớp

Toàn bộ lớp nghiệp vụ nằm trong tầng `backend/models/`. Mỗi lớp đều tuân theo **cùng một pattern**:

| Method | Vai trò |
|--------|---------|
| `__init__()` | Khởi tạo, tự động strip() chuỗi, ép kiểu số |
| `validate()` | Kiểm tra nghiệp vụ, trả `(bool, str)` |
| `from_row(row)` | Static factory — tạo đối tượng từ tuple SQL |
| `to_table_row()` | Trả tuple để hiển thị lên Treeview (Tkinter) |
| `to_dict()` | Xuất dict để truyền vào service/DB |
| `__str__()` | Chuỗi debug thân thiện |

Hai quan hệ **Composition** trong hệ thống:
- `Invoice ◆──► InvoiceItem` — một hóa đơn chứa nhiều dòng sản phẩm
- `StockEntry ◆──► StockItem` — một phiếu nhập chứa nhiều dòng hàng hóa

---

## 1. Customer — Khách hàng

**File:** `backend/models/customer.py`  
**Bảng DB tương ứng:** `khach_hang`

### Thuộc tính

| Thuộc tính | Kiểu | Mô tả |
|------------|------|-------|
| `ma_kh` | `int \| None` | Mã khách hàng (PK, tự tăng) |
| `ten_kh` | `str` | Họ và tên khách hàng *(bắt buộc)* |
| `so_dt` | `str` | Số điện thoại (chỉ chứa chữ số) |
| `dia_chi` | `str` | Địa chỉ |
| `email` | `str` | Email |
| `diem_tich_luy` | `int` | Điểm tích lũy hiện tại, mặc định = 0 |

### Phương thức

| Phương thức | Tham số | Trả về | Mô tả |
|-------------|---------|--------|-------|
| `validate()` | — | `tuple[bool, str]` | Kiểm tra tên không trống, SĐT chỉ chứa chữ số |
| `to_table_row()` | — | `tuple` | Trả 6 giá trị cho Treeview |
| `from_row(row)` *(static)* | `tuple` từ SQL | `Customer` | Factory method từ kết quả query |
| `__str__()` | — | `str` | `[KH#1] Nguyễn Văn A | 0988888888` |

### Ghi chú nghiệp vụ

- `ma_kh = None` có nghĩa là đối tượng chưa được lưu vào DB.
- Hóa đơn cho phép `ma_kh = NULL` (khách lẻ không đăng ký tài khoản).
- Điểm tích lũy được cập nhật qua `lich_su_diem_kh`, không sửa trực tiếp.

---

## 2. Employee — Nhân viên

**File:** `backend/models/employee.py`  
**Bảng DB tương ứng:** `nhan_vien`

### Thuộc tính

| Thuộc tính | Kiểu | Mô tả |
|------------|------|-------|
| `ma_nv` | `int \| None` | Mã nhân viên (PK) |
| `ten_nv` | `str` | Họ và tên *(bắt buộc)* |
| `tai_khoan` | `str` | Tên đăng nhập, tối thiểu 4 ký tự, UNIQUE *(bắt buộc)* |
| `mat_khau` | `str` | Mật khẩu đã hash bcrypt |
| `vai_tro` | `str` | `"admin"` hoặc `"nhanvien"` |
| `so_dt` | `str` | Số điện thoại |
| `trang_thai` | `int` | `1` = hoạt động, `0` = tạm khóa |

### Property (computed)

| Property | Trả về | Mô tả |
|----------|--------|-------|
| `trang_thai_str` | `str` | `"Hoạt động"` hoặc `"Tạm khóa"` |
| `vai_tro_str` | `str` | `"Quản trị"` hoặc `"Nhân viên"` |

### Phương thức

| Phương thức | Mô tả |
|-------------|-------|
| `validate()` | Kiểm tra tên, tài khoản không trống, tài khoản ≥ 4 ký tự |
| `from_row(row)` *(static)* | row = `(ma_nv, ten_nv, tai_khoan, vai_tro, so_dt, trang_thai)` |
| `to_table_row()` | 6 cột: Mã NV, Họ tên, Tài khoản, Vai trò, SĐT, Trạng thái |

### Ghi chú nghiệp vụ

- Mật khẩu **không bao giờ** lưu dạng plain text — luôn hash bcrypt trước khi INSERT.
- Hằng số `VAI_TRO_CHOICES = ["admin", "nhanvien"]` kiểm soát giá trị hợp lệ.
- Tài khoản admin mặc định được tạo trong `db_init.py` với mật khẩu `123456`.

---

## 3. Supplier — Nhà cung cấp *(mới thêm)*

**File:** `backend/models/supplier.py`  
**Bảng DB tương ứng:** `nha_cung_cap`

### Thuộc tính

| Thuộc tính | Kiểu | Mô tả |
|------------|------|-------|
| `ma_ncc` | `int \| None` | Mã nhà cung cấp (PK) |
| `ten_ncc` | `str` | Tên công ty / cá nhân *(bắt buộc)* |
| `nguoi_lh` | `str` | Tên người liên hệ |
| `dia_chi` | `str` | Địa chỉ |
| `so_dt` | `str` | Số điện thoại |
| `email` | `str` | Email liên hệ |
| `website` | `str` | Website |
| `ghi_chu` | `str` | Ghi chú tự do |
| `trang_thai` | `int` | `1` = đang hợp tác, `0` = ngừng hợp tác |

### Property (computed)

| Property | Trả về |
|----------|--------|
| `trang_thai_str` | `"Hoạt động"` hoặc `"Ngừng hợp tác"` |

### Phương thức

| Phương thức | Mô tả |
|-------------|-------|
| `validate()` | Tên NCC không trống; SĐT chỉ chứa chữ số; email phải có `@` |
| `from_row(row)` *(static)* | row = `(ma_ncc, ten_ncc, nguoi_lh, dia_chi, so_dt, email, website, ghi_chu, trang_thai)` |
| `to_table_row()` | 6 cột: Mã NCC, Tên NCC, Người LH, SĐT, Email, Trạng thái |

### Ghi chú nghiệp vụ

- Không xóa cứng nhà cung cấp — dùng `toggle_status()` chuyển `trang_thai = 0`.
- `supplier_service.get_dropdown()` trả `list[(ma_ncc, ten_ncc)]` cho Combobox nhập kho.
- `StockEntry.ma_ncc` tham chiếu đến Supplier; nếu NCC bị xóa → `SET NULL`.

---

## 4. Product — Sản phẩm

**File:** `backend/models/product.py`  
**Bảng DB tương ứng:** `san_pham`, `loai_san_pham`

### Thuộc tính

| Thuộc tính | Kiểu | Mô tả |
|------------|------|-------|
| `ma_sp` | `int \| None` | Mã sản phẩm (PK) |
| `ma_code` | `str` | Mã định danh ngắn (UNIQUE, vd: `SP01`) |
| `ten_sp` | `str` | Tên sản phẩm |
| `ten_loai` | `str` | Tên loại sản phẩm (JOIN từ `loai_san_pham`) |
| `don_vi` | `str` | Đơn vị tính (cây, quyển, ram...) |
| `gia_nhap` | `float` | Giá vốn |
| `gia_ban` | `float` | Giá bán lẻ |
| `ton_kho` | `int` | Số lượng tồn kho hiện tại |
| `mo_ta` | `str` | Mô tả chi tiết |
| `ma_loai` | `int \| None` | FK → `loai_san_pham.ma_loai` |

### Property (computed — tính tự động, không lưu DB)

| Property | Công thức | Mô tả |
|----------|-----------|-------|
| `loi_nhuan` | `gia_ban - gia_nhap` | Lợi nhuận một đơn vị |
| `ty_le_loi_nhuan` | `(loi_nhuan / gia_nhap) × 100` | Phần trăm lợi nhuận |
| `sap_het` | `ton_kho <= 10` | Cảnh báo tồn kho thấp |

### Phương thức

| Phương thức | Mô tả |
|-------------|-------|
| `fmt_gia_ban()` | `"5,000đ"` — format có dấu phẩy |
| `fmt_gia_nhap()` | Tương tự cho giá nhập |
| `to_table_row()` | 7 cột: Mã, Tên, Loại, ĐVT, Giá nhập, Giá bán, Tồn kho |
| `from_row(row)` *(static)* | row 8–9 phần tử tùy DB cũ/mới |

---

## 5. Invoice — Hóa đơn bán hàng

**File:** `backend/models/invoice.py`  
**Bảng DB tương ứng:** `hoa_don`, `chi_tiet_hoa_don`

`Invoice` và `InvoiceItem` tạo thành quan hệ **Composition** — `Invoice` sở hữu danh sách `InvoiceItem`.

---

### 5a. InvoiceItem — Chi tiết hóa đơn

| Thuộc tính | Kiểu | Mô tả |
|------------|------|-------|
| `ma_sp` | `int` | FK → `san_pham.ma_sp` |
| `ten_sp` | `str` | Tên sản phẩm (snapshot tại thời điểm bán) |
| `don_gia` | `float` | Đơn giá tại thời điểm bán |
| `so_luong` | `int` | Số lượng mua |
| `thanh_tien` *(property)* | `float` | `don_gia × so_luong` |

---

### 5b. Invoice — Header hóa đơn

| Thuộc tính | Kiểu | Mô tả |
|------------|------|-------|
| `ma_hd` | `int \| None` | Mã hóa đơn (gán sau khi INSERT) |
| `ma_nv` | `int` | FK → `nhan_vien.ma_nv` |
| `ten_nv` | `str` | Tên nhân viên (snapshot) |
| `ma_kh` | `int \| None` | FK → `khach_hang.ma_kh` (NULL = khách lẻ) |
| `ten_kh` | `str` | Tên khách hàng, mặc định `"Khách lẻ"` |
| `ngay_ban` | `datetime` | Thời điểm tạo hóa đơn (`datetime.now()`) |
| `giam_gia` | `float` | Số tiền giảm giá (đ) |
| `hinh_thuc` | `str` | `"Tiền mặt"` hoặc `"Chuyển khoản"` |
| `items` | `list[InvoiceItem]` | Danh sách sản phẩm trong hóa đơn |

### Property (computed)

| Property | Mô tả |
|----------|-------|
| `tong_tien` | Tổng tiền trước giảm giá = `Σ(thanh_tien)` |
| `thanh_toan` | Số tiền thực trả = `max(0, tong_tien - giam_gia)` |
| `so_mon` | Số dòng sản phẩm trong hóa đơn |

### Phương thức chính

| Phương thức | Mô tả |
|-------------|-------|
| `add_item(ma_sp, ten_sp, don_gia, so_luong=1)` | Thêm sản phẩm; nếu đã có trong hóa đơn → cộng dồn số lượng |
| `remove_item(ma_sp)` | Xóa dòng sản phẩm khỏi hóa đơn |
| `clear()` | Xóa toàn bộ items, reset giảm giá |
| `to_dict()` | Xuất dict gồm header + list items để lưu DB |

---

## 6. StockEntry — Phiếu nhập kho

**File:** `backend/models/stock_entry.py`  
**Bảng DB tương ứng:** `phieu_nhap`, `chi_tiet_phieu_nhap`

Cấu trúc **đối xứng hoàn toàn** với `Invoice` / `InvoiceItem`, nhưng phục vụ luồng nhập hàng thay vì bán hàng.

---

### 6a. StockItem — Chi tiết phiếu nhập

| Thuộc tính | Kiểu | Mô tả |
|------------|------|-------|
| `ma_sp` | `int` | FK → `san_pham.ma_sp` |
| `ten_sp` | `str` | Tên sản phẩm |
| `don_gia` | `float` | Giá nhập của lô hàng này |
| `so_luong` | `int` | Số lượng nhập |
| `thanh_tien` *(property)* | `float` | `don_gia × so_luong` |

---

### 6b. StockEntry — Header phiếu nhập

| Thuộc tính | Kiểu | Mô tả |
|------------|------|-------|
| `ma_phieu` | `int \| None` | Mã phiếu nhập (gán sau INSERT) |
| `ma_nv` | `int` | FK → `nhan_vien.ma_nv` |
| `ten_nv` | `str` | Tên nhân viên lập phiếu |
| `ma_ncc` | `int \| None` | FK → `nha_cung_cap.ma_ncc` (có thể NULL) |
| `ten_ncc` | `str` | Tên nhà cung cấp |
| `ngay_nhap` | `datetime` | Thời điểm lập phiếu |
| `ghi_chu` | `str` | Ghi chú tùy ý |
| `items` | `list[StockItem]` | Danh sách hàng nhập |

### Property (computed)

| Property | Mô tả |
|----------|-------|
| `tong_tien` | Tổng giá trị phiếu nhập = `Σ(thanh_tien)` |
| `so_dong` | Số dòng hàng trong phiếu |

### Sự khác biệt so với Invoice

| | Invoice | StockEntry |
|--|---------|-----------|
| Đối tác | `Customer` (khách hàng) | `Supplier` (nhà cung cấp) |
| Tác động tồn kho | Giảm `ton_kho` | Tăng `ton_kho` |
| Bảng chi tiết | `chi_tiet_hoa_don` | `chi_tiet_phieu_nhap` |
| Có giảm giá | Có (`giam_gia`) | Không |
| Có hạn sử dụng | Không | Có (`han_su_dung`) |

---

## Sơ đồ quan hệ giữa các lớp

```
Customer ◄─── Invoice ◆────► InvoiceItem ────► Product
               (ma_kh)         (ma_sp)

Supplier ◄─── StockEntry ◆──► StockItem ────► Product
               (ma_ncc)         (ma_sp)

Employee ────► Invoice    (ma_nv — nhân viên tạo hóa đơn)
Employee ────► StockEntry (ma_nv — nhân viên lập phiếu nhập)
```

**Chú thích:**
- `◆────►` Composition (phần tử con không tồn tại độc lập)
- `◄────` Association (tham chiếu bằng khóa ngoại)