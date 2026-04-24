PHẦN 1 — MÔ TẢ CHỨC NĂNG ỨNG DỤNG
1. Giới thiệu hệ thống

- Ứng dụng VPP Manager là phần mềm quản lý cửa hàng văn phòng phẩm, được xây dựng nhằm hỗ trợ các hoạt động kinh doanh hàng ngày như quản lý sản phẩm, bán hàng, quản lý khách hàng, nhập kho và thống kê báo cáo.

Hệ thống được thiết kế với mục tiêu:

- Hỗ trợ quản lý cửa hàng một cách hiệu quả và khoa học
- Giảm thiểu sai sót trong quá trình bán hàng và nhập kho
- Cung cấp thông tin trực quan về doanh thu và tình trạng tồn kho
- Tăng tốc độ xử lý và nâng cao trải nghiệm người dùng
2. Đối tượng sử dụng

Hệ thống phục vụ hai nhóm người dùng chính:

2.1. Quản trị viên (Admin)
- Quản lý toàn bộ hệ thống
- Thêm, sửa, xóa sản phẩm
- Xem báo cáo và thống kê
- Quản lý thông tin nhân viên
- Phân quyền người dùng

2.2. Nhân viên (Staff)
- Thực hiện bán hàng
- Tra cứu thông tin sản phẩm
- Thêm và quản lý khách hàng
3. Các chức năng chính

3.1. Đăng nhập hệ thống
- Người dùng nhập tài khoản và mật khẩu
- Hệ thống kiểm tra thông tin đăng nhập
- Xác định quyền truy cập dựa trên vai trò (admin hoặc staff)

3.2. Tổng quan (Dashboard)

Hiển thị các thông tin tổng hợp về hoạt động trong ngày, bao gồm:

- Số lượng hóa đơn đã tạo
- Tổng doanh thu trong ngày
- Tổng số sản phẩm hiện có
- Số lượng sản phẩm sắp hết hàng
- Tổng số khách hàng

Chức năng này giúp người quản lý nhanh chóng nắm bắt tình hình kinh doanh.

3.3. Quản lý sản phẩm

Cho phép thực hiện các thao tác:

- Thêm sản phẩm mới
- Cập nhật thông tin sản phẩm
- Xóa (ẩn) sản phẩm
- Tìm kiếm sản phẩm theo tên hoặc mã

Thông tin sản phẩm bao gồm:

- Mã sản phẩm
- Tên sản phẩm
- Giá nhập và giá bán
- Số lượng tồn kho
- Loại sản phẩm
- Mô tả (nếu có)

3.4. Bán hàng (POS)

Đây là chức năng cốt lõi của hệ thống:

- Lựa chọn sản phẩm từ danh sách
- Thêm sản phẩm vào hóa đơn
- Nhập số lượng
- Tự động tính tổng tiền
- Áp dụng giảm giá (nếu có)
- Thực hiện thanh toán

Sau khi hoàn tất:

- Hóa đơn được lưu vào hệ thống
- Có thể xuất hóa đơn ra file PDF

3.5. Quản lý khách hàng

Cho phép:

- Thêm khách hàng mới
- Cập nhật thông tin khách hàng
- Tìm kiếm theo tên hoặc số điện thoại

Thông tin khách hàng gồm:

- Tên khách hàng
- Số điện thoại
- Địa chỉ
- Điểm tích lũy

3.6. Nhập kho

Chức năng hỗ trợ quản lý hàng hóa đầu vào:

- Tạo phiếu nhập hàng
- Cập nhật số lượng tồn kho
- Lưu trữ lịch sử nhập hàng

Giúp kiểm soát nguồn hàng và đảm bảo dữ liệu tồn kho chính xác.

3.7. Quản lý nhân viên (dành cho Admin)
- Thêm nhân viên mới
- Chỉnh sửa thông tin nhân viên
- Phân quyền (admin hoặc staff)
- Khóa hoặc kích hoạt tài khoản

3.8. Báo cáo và thống kê

Cung cấp các công cụ phân tích dữ liệu:

- Thống kê doanh thu theo ngày
- Danh sách sản phẩm bán chạy
- Xuất dữ liệu ra file Excel
- Hiển thị biểu đồ trực quan
4. Quy trình hoạt động của hệ thống

Quy trình sử dụng hệ thống gồm các bước:

I. Người dùng đăng nhập vào hệ thống

II. Truy cập màn hình tổng quan

III. Thực hiện các nghiệp vụ:
- Bán hàng
- Quản lý sản phẩm
- Nhập kho

IV. Dữ liệu được lưu trữ trong cơ sở dữ liệu

V. Xem báo cáo và thống kê khi cần
5. Công nghệ sử dụng

Hệ thống được xây dựng với các công nghệ sau:

Ngôn ngữ lập trình: Python

Giao diện người dùng: Tkinter / CustomTkinter

Hệ quản trị cơ sở dữ liệu: MySQL