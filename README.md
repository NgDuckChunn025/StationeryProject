# StationeryProject
Phần mềm quản lý cửa hàng văn phòng phẩm bằng Python
<div align="center">

#  Phần Mềm Quản Lý Cửa Hàng Văn Phòng Phẩm
<br/>

> Ứng dụng desktop quản lý toàn diện hoạt động kinh doanh cửa hàng văn phòng phẩm — từ quản lý sản phẩm, bán hàng đến xuất báo cáo PDF chuyên nghiệp.

</div>

---

##  Mục Lục

- [Giới thiệu](#-giới-thiệu)
- [Tính năng](#-tính-năng)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Cài đặt](#-cài-đặt)
- [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng)
- [Ảnh chụp màn hình](#-ảnh-chụp-màn-hình)

---

## Giới Thiệu

**Phần mềm quản lý cửa hàng văn phòng phẩm** là một ứng dụng desktop được xây dựng bằng Python, giúp các chủ cửa hàng dễ dàng quản lý hàng hóa, theo dõi đơn hàng, quản lý thông tin khách hàng và tạo báo cáo kinh doanh trực quan — tất cả trong một giao diện thân thiện, dễ sử dụng.

---

## Tính Năng

| Tính năng | Mô tả |
|---|---|
|  **Đăng nhập / Xác thực** | Hệ thống đăng nhập bảo mật với phân quyền người dùng |
|  **Quản lý sản phẩm** | Thêm, sửa, xóa và tìm kiếm sản phẩm văn phòng phẩm |
|  **Quản lý bán hàng** | Xử lý giao dịch, tạo hóa đơn nhanh chóng |
|  **Quản lý khách hàng** | Lưu trữ và tra cứu thông tin khách hàng |
|  **Báo cáo thống kê** | Báo cáo doanh thu, tồn kho trực quan |
|  **Xuất PDF** | In hóa đơn và báo cáo ra file PDF chuyên nghiệp |

---

## 🛠️ Công Nghệ Sử Dụng

- **Ngôn ngữ:** Python 3.10+
- **Giao diện:** Tkinter / CustomTkinter
- **Cơ sở dữ liệu:** MySQL
- **Xuất PDF:** ReportLab / FPDF
- **Môi trường ảo:** venv

---

##  Cấu Trúc Dự Án

```
📦 stationery-store-manager
├── 📂 frontend/
├── gui/
│   ├── login_ui.py             # Giao diện đăng nhập
│   ├── main_window.py       # Cửa sổ chính của ứng dụng
│   ├── product_ui.py          # Giao diện quản lý sản phẩm
│   ├── sales_ui.py          # Giao diện bán hàng
│   ├── customer_ui.py        # Giao diện quản lý khách hàng
│   └── report_ui.py           # Giao diện báo cáo
├── 📂 backend/
├── models/
│   ├── product.py          # Model sản phẩm
│   └── invoice.py           # Model hóa đơn
├── database/
│   ├── connection.py        # Kết nối cơ sở dữ liệu
│   └── db_init.py           # Khởi tạo schema database
├── modules/
│   ├── auth_service.py          # Logic xác thực người dùng
│   ├── product_service.py  # Logic quản lý sản phẩm
│   ├── sales_service.py  # Logic quản lý bán hàng
│   ├── report_service.py           # Logic tạo báo cáo
│   └── pdf_exporter.py          # Xuất file PDF
│
├──  main.py               # Điểm khởi chạy ứng dụng
├──  requirements.txt      # Danh sách thư viện cần thiết
├──  .gitignore
└──  README.md
```

---

##  Cài Đặt

### Yêu cầu hệ thống

- Python **3.10** trở lên
- pip

### Các bước cài đặt

**1. Clone repository**
```bash
git clone https://github.com/NgDuckChunn205/StationeryProject.git
cd StationeryProject
```

**2. Tạo và kích hoạt môi trường ảo**
```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt (Windows)
.venv\Scripts\activate

# Kích hoạt (macOS/Linux)
source .venv/bin/activate
```

**3. Cài đặt thư viện**
```bash
pip install -r requirements.txt
```

**4. Chạy ứng dụng**
```bash
python main.py
```

---

## Hướng Dẫn Sử Dụng

1. **Đăng nhập** bằng tài khoản quản trị viên
2. Từ **cửa sổ chính**, chọn chức năng cần dùng trên thanh điều hướng
3. **Quản lý sản phẩm:** Thêm/sửa/xóa mặt hàng, cập nhật số lượng tồn kho
4. **Bán hàng:** Chọn sản phẩm, nhập số lượng, tạo hóa đơn và xuất PDF
5. **Báo cáo:** Xem thống kê doanh thu theo ngày/tháng/năm

---

##  Ảnh Chụp Màn Hình

> *(Cập nhật sau khi hoàn thiện giao diện)*

---
