# Mô tả Cơ sở dữ liệu — VPP Manager
> **HQTCSDL:** MySQL 8.0+ · **Charset:** utf8mb4 · **Collation:** utf8mb4_unicode_ci  
> **Tổng số bảng:** 13 · **FK constraints:** 15 · **ERD:** không thay đổi sau khi fix code

---

## Tổng quan nhóm bảng

| Nhóm | Bảng | Chức năng |
|------|------|-----------|
| **Danh mục** | `loai_san_pham`, `san_pham`, `nha_cung_cap` | Quản lý hàng hóa và đối tác |
| **Nhân sự** | `nhan_vien` | Tài khoản đăng nhập, phân quyền |
| **Khách hàng** | `khach_hang`, `lich_su_diem_kh` | CRM, tích điểm |
| **Bán hàng** | `hoa_don`, `chi_tiet_hoa_don` | Giao dịch POS |
| **Nhập kho** | `phieu_nhap`, `chi_tiet_phieu_nhap` | Nhập hàng từ NCC |
| **Trả hàng** | `phieu_tra_hang`, `chi_tiet_phieu_tra` | Hoàn trả |
| **Hệ thống** | `cau_hinh` | Cài đặt cửa hàng (key-value) |

---

## 1. loai_san_pham — Loại sản phẩm

Bảng danh mục phân nhóm sản phẩm (Bút, Vở, Giấy, Dụng cụ...).

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_loai` | `INT` | PK, AUTO_INCREMENT | Mã loại |
| `ten_loai` | `VARCHAR(100)` | NOT NULL | Tên loại |
| `mo_ta` | `VARCHAR(255)` | — | Mô tả thêm |

**Quan hệ:** `1 loai_san_pham ──► nhiều san_pham`

---

## 2. san_pham — Sản phẩm

Bảng trung tâm — lưu toàn bộ hàng hóa kinh doanh.

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_sp` | `INT` | PK, AUTO_INCREMENT | Mã sản phẩm |
| `ma_code` | `VARCHAR(20)` | UNIQUE, NOT NULL | Mã ngắn (SP01...) |
| `ten_sp` | `VARCHAR(200)` | NOT NULL | Tên sản phẩm |
| `ma_loai` | `INT` | FK → `loai_san_pham` | Phân loại |
| `don_vi` | `VARCHAR(50)` | — | Đơn vị tính |
| `gia_nhap` | `DECIMAL(15,0)` | DEFAULT 0 | Giá vốn (đồng) |
| `gia_ban` | `DECIMAL(15,0)` | DEFAULT 0 | Giá bán lẻ (đồng) |
| `ton_kho` | `INT` | DEFAULT 0 | Tồn kho hiện tại |
| `ton_kho_min` | `INT` | DEFAULT 10 | Ngưỡng cảnh báo tồn thấp |
| `trang_thai` | `TINYINT(1)` | DEFAULT 1 | 1=đang bán, 0=ẩn (soft delete) |
| `mo_ta` | `TEXT` | — | Mô tả chi tiết |
| `hinh_anh` | `VARCHAR(500)` | — | Đường dẫn ảnh |
| `ngay_tao` | `DATETIME` | DEFAULT NOW() | Thời điểm thêm vào |

**Lưu ý quan trọng:**
- `ton_kho` tự động cập nhật: `-= so_luong` khi bán, `+= so_luong` khi nhập
- Không DELETE sản phẩm — chỉ set `trang_thai=0` để giữ lịch sử hóa đơn

---

## 3. khach_hang — Khách hàng

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_kh` | `INT` | PK, AUTO_INCREMENT | Mã khách hàng |
| `ten_kh` | `VARCHAR(200)` | — | Họ và tên |
| `so_dt` | `VARCHAR(20)` | — | Số điện thoại |
| `dia_chi` | `VARCHAR(255)` | — | Địa chỉ |
| `email` | `VARCHAR(100)` | — | Email |
| `ngay_sinh` | `DATE` | — | Ngày sinh |
| `gioi_tinh` | `TINYINT(1)` | — | 1=Nam, 0=Nữ |
| `diem_tich_luy` | `INT` | DEFAULT 0 | Tổng điểm hiện tại |
| `hang_khach_hang` | `VARCHAR(20)` | DEFAULT 'Thường' | Thường/Bạc/Vàng/Bạch Kim |
| `tong_chi_tieu` | `DECIMAL(15,0)` | DEFAULT 0 | Tổng tiền đã mua |
| `ngay_tao` | `DATETIME` | DEFAULT NOW() | Ngày đăng ký |

**Quan hệ:**
- `1 khach_hang ──► nhiều hoa_don` (ON DELETE SET NULL — xóa KH vẫn giữ hóa đơn)
- `1 khach_hang ──► nhiều lich_su_diem_kh` (ON DELETE CASCADE)

---

## 4. nhan_vien — Nhân viên

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_nv` | `INT` | PK, AUTO_INCREMENT | Mã nhân viên |
| `ten_nv` | `VARCHAR(200)` | — | Họ và tên |
| `tai_khoan` | `VARCHAR(50)` | UNIQUE | Tên đăng nhập |
| `mat_khau` | `VARCHAR(255)` | — | Mật khẩu hash bcrypt |
| `vai_tro` | `VARCHAR(20)` | DEFAULT 'nhanvien' | `admin` hoặc `nhanvien` |
| `so_dt` | `VARCHAR(20)` | — | Số điện thoại |
| `email` | `VARCHAR(100)` | — | Email nội bộ |
| `dia_chi` | `VARCHAR(300)` | — | Địa chỉ |
| `ngay_vao` | `DATE` | — | Ngày vào làm |
| `trang_thai` | `TINYINT(1)` | DEFAULT 1 | 1=hoạt động, 0=tạm khóa |

**Phân quyền:**
- `admin` — toàn quyền, thấy menu Nhân viên và Nhà cung cấp
- `nhanvien` — Bán hàng, Sản phẩm, Khách hàng, Nhập kho, Báo cáo

---

## 5. nha_cung_cap — Nhà cung cấp *(mới hoàn chỉnh)*

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_ncc` | `INT` | PK, AUTO_INCREMENT | Mã NCC |
| `ten_ncc` | `VARCHAR(200)` | NOT NULL | Tên công ty/cá nhân |
| `nguoi_lh` | `VARCHAR(100)` | — | Người liên hệ |
| `dia_chi` | `VARCHAR(300)` | — | Địa chỉ |
| `so_dt` | `VARCHAR(20)` | — | Số điện thoại |
| `email` | `VARCHAR(100)` | — | Email liên hệ |
| `website` | `VARCHAR(200)` | — | Website |
| `ghi_chu` | `TEXT` | — | Ghi chú |
| `trang_thai` | `TINYINT(1)` | DEFAULT 1 | 1=đang hợp tác, 0=ngừng |
| `ngay_tao` | `DATETIME` | DEFAULT NOW() | Ngày bắt đầu hợp tác |

**Quan hệ:** `1 nha_cung_cap ──► nhiều phieu_nhap` (ON DELETE SET NULL)

---

## 6. hoa_don — Hóa đơn bán hàng (header)

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_hd` | `INT` | PK, AUTO_INCREMENT | Mã hóa đơn |
| `ma_nv` | `INT` | FK → `nhan_vien`, NULL OK | Nhân viên thu ngân |
| `ma_kh` | `INT` | FK → `khach_hang`, NULL OK | Khách hàng (NULL=khách lẻ) |
| `tong_tien` | `DECIMAL(15,0)` | DEFAULT 0 | Tổng trước giảm giá |
| `giam_gia` | `DECIMAL(15,0)` | DEFAULT 0 | Số tiền giảm |
| `thanh_toan` | `DECIMAL(15,0)` | DEFAULT 0 | Số tiền thực thu |
| `hinh_thuc` | `VARCHAR(50)` | DEFAULT 'Tiền mặt' | Tiền mặt / Chuyển khoản |
| `ngay_ban` | `DATETIME` | DEFAULT NOW() | Thời điểm giao dịch |
| `trang_thai` | `VARCHAR(20)` | DEFAULT 'Hoàn thành' | Trạng thái hóa đơn |
| `ghi_chu` | `TEXT` | — | Ghi chú |

**FK:** `ma_nv` và `ma_kh` đều ON DELETE SET NULL — xóa NV/KH không mất hóa đơn.

---

## 7. chi_tiet_hoa_don — Chi tiết hóa đơn

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_ct` | `INT` | PK, AUTO_INCREMENT | Mã chi tiết |
| `ma_hd` | `INT` | FK → `hoa_don` **CASCADE** | Hóa đơn chứa |
| `ma_sp` | `INT` | FK → `san_pham` **RESTRICT** | Sản phẩm |
| `so_luong` | `INT` | DEFAULT 1 | Số lượng mua |
| `don_gia` | `DECIMAL(15,0)` | DEFAULT 0 | Giá tại thời điểm bán |
| `ghi_chu` | `VARCHAR(200)` | — | Ghi chú dòng |

**Lưu ý:** `don_gia` chốt tại thời điểm bán — không thay đổi dù giá SP sau này thay đổi.

---

## 8. phieu_nhap — Phiếu nhập kho (header)

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_phieu` | `INT` | PK, AUTO_INCREMENT | Mã phiếu nhập |
| `ma_ncc` | `INT` | FK → `nha_cung_cap`, NULL OK | Nhà cung cấp |
| `ma_nv` | `INT` | FK → `nhan_vien`, NULL OK | Nhân viên lập phiếu |
| `ngay_nhap` | `DATETIME` | DEFAULT NOW() | Thời điểm nhập |
| `tong_tien` | `DECIMAL(15,0)` | DEFAULT 0 | Tổng giá trị lô hàng |
| `da_thanh_toan` | `TINYINT(1)` | DEFAULT 0 | Đã thanh toán cho NCC chưa |
| `ghi_chu` | `TEXT` | — | Ghi chú |

---

## 9. chi_tiet_phieu_nhap — Chi tiết phiếu nhập

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_ct` | `INT` | PK, AUTO_INCREMENT | Mã chi tiết |
| `ma_phieu` | `INT` | FK → `phieu_nhap` **CASCADE** | Phiếu nhập |
| `ma_sp` | `INT` | FK → `san_pham` **RESTRICT** | Sản phẩm nhập |
| `so_luong` | `INT` | DEFAULT 1 | Số lượng nhập |
| `don_gia` | `DECIMAL(15,0)` | DEFAULT 0 | Giá nhập lô này |
| `han_su_dung` | `DATE` | — | Hạn sử dụng (nếu có) |

---

## 10. phieu_tra_hang — Phiếu trả hàng (header)

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_phieu_tra` | `INT` | PK, AUTO_INCREMENT | Mã phiếu trả |
| `ma_hd_goc` | `INT` | FK → `hoa_don` **RESTRICT** | Hóa đơn gốc |
| `ma_nv` | `INT` | FK → `nhan_vien` **RESTRICT** | Nhân viên xử lý |
| `ngay_tra` | `DATETIME` | DEFAULT NOW() | Thời điểm trả |
| `ly_do` | `VARCHAR(300)` | — | Lý do trả |
| `tong_hoan` | `DECIMAL(15,0)` | DEFAULT 0 | Tổng tiền hoàn |
| `hinh_thuc_hoan` | `VARCHAR(50)` | DEFAULT 'Tiền mặt' | Hình thức hoàn tiền |
| `ghi_chu` | `TEXT` | — | Ghi chú |

---

## 11. chi_tiet_phieu_tra — Chi tiết phiếu trả

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_ct` | `INT` | PK, AUTO_INCREMENT | Mã chi tiết |
| `ma_phieu_tra` | `INT` | FK → `phieu_tra_hang` **CASCADE** | Phiếu trả |
| `ma_sp` | `INT` | FK → `san_pham` **RESTRICT** | Sản phẩm trả |
| `so_luong_tra` | `INT` | DEFAULT 1 | Số lượng trả |
| `don_gia` | `DECIMAL(15,0)` | DEFAULT 0 | Đơn giá hoàn (bằng giá bán gốc) |
| `ly_do_chi` | `VARCHAR(200)` | — | Lý do riêng từng dòng |

---

## 12. lich_su_diem_kh — Lịch sử điểm khách hàng

Ghi lại mỗi lần cộng/trừ điểm tích lũy.

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_ls` | `INT` | PK, AUTO_INCREMENT | Mã lịch sử |
| `ma_kh` | `INT` | FK → `khach_hang` **CASCADE** | Khách hàng |
| `loai` | `VARCHAR(20)` | NOT NULL | `"cong"` hoặc `"tru"` |
| `so_diem` | `INT` | NOT NULL | Số điểm thay đổi (luôn dương) |
| `ly_do` | `VARCHAR(200)` | — | Mô tả lý do |
| `ma_hd` | `INT` | FK → `hoa_don`, NULL OK | Hóa đơn phát sinh điểm |
| `ngay_ghi` | `DATETIME` | DEFAULT NOW() | Thời điểm ghi |

**Quy tắc:** cứ 10.000đ mua hàng → 1 điểm (cấu hình trong bảng `cau_hinh`).

---

## 13. cau_hinh — Cấu hình hệ thống

Bảng key-value lưu tham số cài đặt. **Đứng độc lập, không có FK.**

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| `ma_ch` | `INT` | PK, AUTO_INCREMENT | Mã cấu hình |
| `ten_khoa` | `VARCHAR(100)` | UNIQUE, NOT NULL | Tên khóa |
| `gia_tri` | `TEXT` | — | Giá trị |
| `mo_ta` | `VARCHAR(255)` | — | Giải thích |
| `ngay_capnhat` | `DATETIME` | ON UPDATE NOW() | Lần cập nhật cuối |

**Các khóa mặc định:**

| `ten_khoa` | Giá trị mặc định | Mô tả |
|------------|-----------------|-------|
| `ten_cua_hang` | Cửa Hàng VPP | Tên in trên hóa đơn |
| `dia_chi` | 123 Đường ABC | Địa chỉ cửa hàng |
| `so_dien_thoai` | 028 1234 5678 | SĐT in trên hóa đơn |
| `ty_le_tich_diem` | 10000 | Số tiền/1 điểm |
| `canh_bao_ton_kho` | 10 | Ngưỡng tồn kho cảnh báo |

---

## Tổng hợp 15 Foreign Key Constraints

| Bảng con | Cột FK | Bảng cha | ON DELETE | Lý do |
|----------|--------|----------|-----------|-------|
| `san_pham` | `ma_loai` | `loai_san_pham` | RESTRICT | Không xóa loại nếu còn SP |
| `hoa_don` | `ma_nv` | `nhan_vien` | SET NULL | Giữ hóa đơn kể cả khi NV nghỉ |
| `hoa_don` | `ma_kh` | `khach_hang` | SET NULL | Giữ hóa đơn kể cả khi xóa KH |
| `chi_tiet_hoa_don` | `ma_hd` | `hoa_don` | CASCADE | Xóa hóa đơn → xóa chi tiết |
| `chi_tiet_hoa_don` | `ma_sp` | `san_pham` | RESTRICT | Không xóa SP có trong hóa đơn |
| `phieu_nhap` | `ma_ncc` | `nha_cung_cap` | SET NULL | Giữ phiếu nhập kể cả khi xóa NCC |
| `phieu_nhap` | `ma_nv` | `nhan_vien` | SET NULL | Giữ phiếu nhập kể cả khi NV nghỉ |
| `chi_tiet_phieu_nhap` | `ma_phieu` | `phieu_nhap` | CASCADE | Xóa phiếu → xóa chi tiết |
| `chi_tiet_phieu_nhap` | `ma_sp` | `san_pham` | RESTRICT | Không xóa SP đã nhập kho |
| `phieu_tra_hang` | `ma_hd_goc` | `hoa_don` | RESTRICT | Không xóa hóa đơn còn phiếu trả |
| `phieu_tra_hang` | `ma_nv` | `nhan_vien` | RESTRICT | Giữ nguyên nghiệp vụ trả hàng |
| `chi_tiet_phieu_tra` | `ma_phieu_tra` | `phieu_tra_hang` | CASCADE | Xóa phiếu trả → xóa chi tiết |
| `chi_tiet_phieu_tra` | `ma_sp` | `san_pham` | RESTRICT | Không xóa SP trong phiếu trả |
| `lich_su_diem_kh` | `ma_kh` | `khach_hang` | CASCADE | Xóa KH → xóa lịch sử điểm |
| `lich_su_diem_kh` | `ma_hd` | `hoa_don` | SET NULL | Giữ lịch sử điểm dù hóa đơn bị xóa |

**Giải thích chiến lược ON DELETE:**
- **CASCADE** — bảng chi tiết: xóa header → tự xóa detail theo (nhất quán dữ liệu)
- **SET NULL** — khi entity cha có thể bị xóa nhưng vẫn muốn giữ bản ghi giao dịch
- **RESTRICT** — bảo vệ nghiệp vụ quan trọng: ngăn xóa khi còn dữ liệu liên kết

---

## File migration
| File | Chức năng |
|------|-----------|
| `db_init.py` | Tạo database và 13 bảng lần đầu |
| `db_migrate.py` | Thêm cột/bảng khi nâng cấp phiên bản |
| `db_migrate_fk.py` | Thêm 15 FK constraints (kiểm tra trước khi thêm, chạy lại an toàn) |