**Phân tích chi tiết yêu cầu & tiêu chí nghiệm thu (Acceptance Criteria)
cho tính năng Tạo lịch họp**

**I.Yêu cầu người ( User Story )**

- **Tiêu đề:** Quản lý lịch họp.

- **Nhân viên / Quản lý** phần mềm.

- Muốn tạo, xem, cập nhật, hủy và nhận thông báo về các cuộc họp trên hệ
  thống.

- Để lên lịch,mời nhân viên tham gia cuộc họp, chia sẻ tài liệu và nhận
  thông báo nhắc lịch tự, tránh xung đột lịch trình và nắm bắt kịp thời
  thông tin cuộc họp.

**II.Tiêu chí nghiệm thu ( Acceptance Criteria )**

**AC1. Hiển thị form tạo lịch họp.**

**1.Nhập thông tin bắt buộc và hợp lệ.**

- Người đang ở giao diện lịch.

- Ở đó người dùng nhấp vào nút " **Tạo lịch họp mới**".

**2.Hệ thống hiển thị giao diện và trường dữ liệu:**

- Hệ thống hiển thị biểu mẫu bao gồm các trường:

  - Tiêu đề cuộc họp (*Bắt buộc*)

  - Ngày & Giờ bắt đầu - Giờ kết thúc (*Bắt buộc*)

  - Hình thức họp (Online / Offline - *Bắt buộc*)

  - Địa điểm / Phòng họp (Nếu chọn Offline) hoặc Link cuộc họp (Google
    Meet/Teams/Zoom nếu chọn Online)

  - Danh sách người tham gia (*Bắt buộc*, nhập email hoặc chọn thành
    viên trong hệ thống)

  - Mô tả / Nội dung cuộc họp (*Thường*)

  - Tệp đính kèm (Tài liệu họp - *Tùy chọn*)

  - Đặt lịch nhắc nhở (Ví dụ: trước 15 phút, 30 phút, 1 giờ).

**3.Xác thực dữ liệu.**

- Thời gian bắt đầu phải lớn hơn thời gian hiện tại.

- Thời gian kết thúc phải sau thời gian bắt đầu.

- Kiểm tra trùng lịch: Hệ thống cảnh báo nếu phòng họp hoặc người tham
  gia chính bị trùng lịch vào khung giờ đó.

**4.Kết quả:**

- Sau khi bấm \"Tạo\", hệ thống lưu cuộc họp và gửi email/thông báo mời
  tham gia đến tất cả người tham gia.

**AC2. Xem danh sách và chi tiết lịch họp.**

**1.Chế độ hiển thị:**

- Cho phép xem theo chế độ Lịch (Ngày / Tuần / Tháng) hoặc Chế độ Danh
  sách.

- Phân biệt trạng thái cuộc họp bằng màu sắc (Sắp diễn ra, Đang diễn ra,
  Đã kết thúc, Đã hủy).

**2.Chi tiết cuộc họp:**

- Khi nhấn vào một cuộc họp, người dùng xem được toàn bộ thông tin: Tiêu
  đề, thời gian, địa điểm/link, danh sách người tham gia và trạng thái
  phản hồi của họ (Đã đồng ý / Từ chối / Chưa phản hồi), tài liệu đính
  kèm.

**AC3. Kiểm tra trùng lịch người tham gia.**

- Người dùng chọn danh sách người tham gia bao gồm Nhân viên A.

- Ở khung giờ được chọn trùng với một cuộc họp khác mà nhân viên A đã
  xác nhận tham gia.

- Hệ thống hiển thị cảnh báo: *\"Nhân viên \[Tên A\] đã có lịch họp
  \[Tên cuộc họp trùng\] trong khung giờ này.\"*

- Hệ thống cho phép người tạo quyết định: **Vẫn tiếp tục tạo** hay
  **Chọn giờ khác**.

**AC4. Kiểm tra trùng tài nguyên cuộc họp.**

- Hình thức họp là Offline và người dùng chọn Phòng họp A.

- Ở phòng họp A đã được đặt bởi một cuộc họp khác trong cùng khung giờ.

- Hệ thống ngăn không cho tạo và hiển thị lỗi: *\"Phòng họp A đã được
  bận từ \[Giờ bắt đầu\] đến \[Giờ kết thúc\]. Vui lòng chọn phòng khác
  hoặc đổi khung giờ.\"*

**AC5. Thời gian họp trong quá khứ**

- Người dùng chọn Thời gian bắt đầu nhỏ hơn thời gian hiện tại của hệ
  thống.

- Hệ thống hiển thị thông báo lỗi: *\"Thời gian bắt đầu cuộc họp không
  được nằm trong quá khứ.\"*

**AC6. Phản hồi lời mời họp.**

**1.Đồng ý / Từ chối / Phân vân**

- Người tham gia nhận được thông báo/email mời họp.

- Người tham gia mở chi tiết cuộc họp và chọn một trong các hành động:

  - Tham gia (Accept)

  - Từ chối (Decline) (Kèm trường nhập lý do - Tùy chọn)

  - Có thể (Tentative)

- Hệ thống cập nhật trạng thái phản hồi của người đó.

- Cập nhật danh sách phản hồi thời gian thực (Real-time) trên màn hình
  của Người tổ chức.

**AC7. Chỉnh sửa và Hủy lịch họp.**

**1.Phân quyền chỉnh sửa.**

- Người dùng A là thành viên tham gia nhưng **không phải** là Người tạo
  hoặc Admin.

- Nút Chỉnh sửa và Hủy cuộc họp sẽ bị ẩn hoặc vô hiệu hóa đối với Người
  dùng A.

**2.Cập nhật lịch họp và gửi thông báo thay đổi.**

- Người tạo thay đổi Thời gian hoặc Địa điểm/Link họp.

- Bấm nút \"Cập nhật\".

- Hệ thống lưu thông tin mới.

- Gửi email/thông báo cập nhật có gắn nhãn \[UPDATE\] đến tất cả người
  tham gia.

- Tự động reset trạng thái phản hồi của người tham gia về **" chưa phản
  hồi\"** nếu thời gian họp bị thay đổi.

**3.Hủy cuộc họp.**

- Người tạo bấm nút \"Hủy cuộc họp\".

- Nhập lý do hủy vào popup xác nhận và bấm \"Xác nhận hủy\".

- Trạng thái cuộc họp chuyển thành "**Đã hủy\".**

- Cuộc họp hiển thị gạch ngang hoặc ẩn trên lịch tùy theo cài đặt bộ
  lọc.

- Gửi email/thông báo hủy kèm lý do đến tất cả người tham gia.

**AC8. Hiển thị lịch và nhắc nhỏ.**

**1.Chế độ xem Lịch.**

- Người dùng truy cập màn hình Quản lý lịch họp.

- Hệ thống hỗ trợ chuyển đổi linh hoạt giữa các chế độ:

  - **Chế độ Ngày (Day view)**

  - **Chế độ Tuần (Week view)**

  - **Chế độ Tháng (Month view)**

  - **Dạng Danh sách (List view)**

- Cho phép lọc lịch họp theo: **Lịch của tôi, Lịch phòng họp, Trạng thái
  (Đã xác nhận / Đã hủy)**.

**2.Hệ thống nhắc nhở tự động.**

- Cuộc họp có thiết lập nhắc nhở trước 15 phút (mặc định: 15 phút).

- Thời gian hiện tại đạt mốc (**Thời gian bắt đầu - X phút**).

- Hệ thống tự động gửi thông báo trên trình duyệt/ứng dụng di động
  và/hoặc Email nhắc nhở.

- Thông báo bao gồm: Tiêu đề họp, Thời gian, Nút bấm \"**Tham gia
  ngay**\" (Trỏ trực tiếp đến Link họp online nếu là cuộc họp Online).

**III.Yêu cầu phi chức năng.**

### **1. Yêu cầu về Hiệu năng.**

- **Thời gian phản hồi:**

  - Màn hình xem lịch (chế độ Ngày/Tuần/Tháng) phải tải xong dữ liệu
    trong vòng **\< 1.5 giây** cho quy mô dưới 1.000 cuộc họp/tháng.

  - Thao tác tạo/sửa/hủy cuộc họp phải trả về kết quả cho người dùng
    trong **\< 1 giây**.

  - Kiểm tra trùng lịch (phòng họp / nhân sự).

- **Thông báo:**

  - Thông báo đếm ngược (nhắc trước 15 phút) phải được hệ thống đẩy
    (Thông báo/Email) đúng thời điểm.

  - Email thông báo mời họp hoặc hủy họp phải đến hộp thư người nhận
    trong vòng **\< 3 phút** kể từ khi người tạo thực hiện thao tác.

- **Tải hệ thống:**

  - Hệ thống phải chịu tải được tối thiểu **500 người dùng truy cập đồng
    thời (Concurrent Users)** vào các khung giờ cao điểm (đầu giờ sáng,
    đầu tuần) mà không bị treo/giật lag.

### **2. Yêu cầu về Bảo mật & Quyền riêng tư.**

- **Phân quyền truy cập:**

  - Mức cuộc họp: Chỉ **Người tạo** hoặc **Admin** mới có quyền Sửa/Xóa
    cuộc họp.

  - Mức tài liệu: Chỉ những người có tên trong **Danh sách tham gia**
    mới có quyền xem nội dung chi tiết và tải file đính kèm của cuộc họp
    đó.

  - Cuộc họp Riêng tư: Cho phép đánh dấu cuộc họp là \"**Riêng tư**\"
    --- các nhân viên khác xem lịch chỉ thấy trạng thái \"**Bận**\" chứ
    không thấy tiêu đề hay nội dung họp.

### **3. Yêu cầu về Khả năng Tích hợp.**

- **Đồng bộ Lịch ngoại bạ:**

  - Cho phép xuất dữ liệu lịch dưới dạng **iCal (.ics)** hoặc đồng bộ 2
    chiều (Two-way sync) với Google Calendar và Microsoft Outlook.

- **Tích hợp Nền tảng Họp Online (Video Conferencing Integration):**

  - Tự động khởi tạo và nhúng link phòng họp (Google Meet / Microsoft
    Teams / Zoom API) ngay khi chọn hình thức họp \"Online\".

- **Tích hợp Kênh thông báo:**

  - Tích hợp gửi thông báo qua Email (SMTP/SendGrid), App Mobile
    (Firebase Cloud Messaging), và ChatOps nội bộ (Slack / Telegram Bot
    / Zalo ZNS nếu có nhu cầu).

### **4. Yêu cầu về Khả năng Mở rộng & Khả dụng.**

- **Độ sẵn sàng:**

  - Cam kết thời gian hoạt động **Uptime đạt 99.9%** (cho phép thời gian
    bảo trì tối đa khoảng 8.76 giờ/năm).

- **Khả năng sao lưu & Phục hồi:**

  - Dữ liệu lịch họp phải được **Backup tự động hàng ngày**.

  - Thời gian phục hồi dữ liệu khi gặp sự cố **\< 2 giờ**.

  - Mức độ mất mát dữ liệu cho phép **\< 15 phút**.

- **Khả năng mở rộng:**

  - Cấu trúc hệ thống phải cho phép mở rộng linh hoạt dung lượng lưu trữ
    tài liệu đính kèm và quy mô người dùng tăng gấp 5 lần mà không cần
    thay đổi kiến trúc core.

### **5. Yêu cầu về Giao diện & Trải nghiệm.**

- **Giao diện đáp ứng:**

  - Hiển thị tối ưu và mượt mà trên cả máy tính (Desktop/Laptop), Bảng
    điều khiển (Tablet) và Điện thoại thông minh (iOS / Android).

- **Trải nghiệm người dùng:**

  - Thao tác đặt lịch cơ bản không quá **3 bước** nhấp chuột.

  - Hỗ trợ giao diện sáng/tối (Light/Dark mode) và ngôn ngữ Đa ngôn ngữ
    (Tối thiểu là **Tiếng Việt** và **Tiếng Anh**).

  - Hiển thị trực quan trạng thái trùng lịch bằng màu sắc rõ ràng (Đỏ:
    Trùng/Bận, Xanh: Rảnh).
