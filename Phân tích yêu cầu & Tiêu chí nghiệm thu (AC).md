**Phân tích yêu cầu & Tiêu chí nghiệm thu Acceptance Criteria cho Hệ Thống Quản Lý Lịch Họp.**

### **I.Yêu cầu người dùng ( User Story ).**

- **Tiêu đề:** Quản lý và Điều hành Lịch họp Hệ thống ICTU.

- **Tư cách:** Ban Giám hiệu / Lãnh đạo Các Khoa, Trung tâm / Cán bộ quản lý khoa/ Chuyên viên Văn phòng Trường ICTU, Quản trị cơ sở vật chất.

- **Muốn:** Đặt lịch họp, đăng ký tài nguyên phòng họp/thiết bị, kiểm tra trùng lịch dạy, phê duyệt lịch họp và nhận thông báo đồng bộ

- **Kết quả:** Đảm bảo các cuộc họp hành chính, hội đồng bảo vệ đồ án, họp chuyên môn diễn ra hanh thông, tránh xung đột thời khóa biểu và tối ưu hóa hạ tầng công nghệ của nhà trường.

**II.Tiêu chí nghiệm thu ( Acceptance Criteria ).**

### **MODULE 1: QUẢN LÝ VÀ ĐẶT LỊCH HỌP.**

#### **US-ICTU-01: Đặt lịch họp và tích hợp Thời khóa biểu ICTU.**

- **Tư cách:** Giảng viên / Cán bộ quản lý Khoa.

- **Muốn:** Tạo cuộc họp và tự động kiểm tra trùng Thời khóa biểu giảng dạy.

- **Kết quả:** Tránh việc xếp lịch họp vào giờ giảng dạy của thầy cô trên lớp.

- **AC 1.1.1 Kiểm tra trùng TKB theo Kíp dạy:**

  - Người dùng nhập thời gian họp và danh sách giảng viên tham gia qua Email dạng dtc@ictu.edu.vn.

  - Bấm nút "Kiểm tra khả dụng".

  - Hệ thống gửi yêu cầu API sang Cổng đào tạo (dtc.ictu.edu.vn) để truy vấn TKB theo các kíp dạy:

    - Kíp 1: 06:45 - 09:10 \| Kíp 2: 09:20 - 11:45

    - Kíp 3: 13:00 - 15:25 \| Kíp 4: 15:35 - 18:00

  - Trả về danh sách giảng viên bận kèm chi tiết: Tên Giảng viên, Mã Lớp HP, Tên môn học, Phòng học bận.

- **AC 1.1.2 Xử lý khi phát hiện trùng TKB:**

  - Phát hiện có ít nhất 01 giảng viên trùng kíp dạy.

  - Hệ thống hiển thị Modal cảnh báo danh sách trùng.

  - Cho phép Người tạo chọn 1 trong 3 giải pháp:

    - *Bỏ qua và tiếp tục tạo* (Hệ thống ghi nhận trạng thái Giảng viên đó là Xung đột lịch).

    - *Đổi danh sách khách mời*.

    - *Chọn khung giờ/ngày khác*.

#### **US-ICTU-02: Quản lý và Phê duyệt Phòng họp Tòa nhà ICTU.**

- **Tư cách:** Chuyên viên Văn phòng Trường / Quản trị Cơ sở vật chất

- **Muốn:** Phê duyệt việc cấp phòng họp/hội trường và quản lý thiết bị công nghệ

- **Kết quả:** Tối ưu hóa việc sử dụng cơ sở vật chất tòa nhà C1, C6.

- **AC 1.2.1 Phân cấp phê duyệt tự động vs thủ công:**

  - Người dùng gửi yêu cầu đặt lịch.

  - Kiểm tra meeting_type và room_id:

    - Nếu phòng họp thuộc quản lý nội bộ Khoa (Phòng họp Khoa C6) → Tự động phê duyệt.

    - Nếu là *Hội trường*, *Phòng họp BGH Tòa C6*, hoặc *Phòng Studio Smart-class* → Đưa vào hàng chờ phê duyệt.

  - Gửi thông báo đến Email của Trưởng Văn phòng Trường để duyệt.

- **AC 1.2.2 Đặt thiết bị và thông báo bộ phận hỗ trợ Kỹ thuật:**

  - Cuộc họp đăng ký tại Hội trường và cần chuẩn bị: Micro không dây, Máy chiếu LED, Hệ thống Video, Kỹ thuật viên trực.

  - Lịch họp chuyển trạng thái tự động.

  - Tự động tạo 01 Ticket công việc gửi đến Dashboard của *Trung tâm Máy tính & Mạng / Phòng Quản trị CSVC* để phân công nhân sự hỗ trợ trước buổi họp 30 phút.

### **MODULE 2: XÁC THỰC, BẢO MẬT VÀ PHÂN QUYỀN.**

#### **US-ICTU-03: Tích hợp SSO và Bảo mật tài liệu họp.**

- **Tư cách:** Chuyên viên Bảo mật / Quản trị viên Hệ thống.

- **Muốn:** Đồng bộ tài khoản SSO ICTU và phân quyền truy cập tài liệu nghiêm ngặt.

- **Kết quả:** Đảm bảo an toàn thông tin nội bộ của nhà trường.

- **AC 2.1.1 Xác thực SSO Microsoft Azure / Google Edu ICTU:**

  - Người dùng truy cập hệ thống.

  - Chọn "Đăng nhập bằng tài khoản ICTU".

  - Chuyển hướng qua cổng OAuth2 / OpenID Connect của Trường.

  - Hệ thống tự động phân vai trò dựa vào đuôi email và dữ liệu AD:

    - @ictu.edu.vn → Role: LECTURER / STAFF.

    - @student.ictu.edu.vn → Role: STUDENT.

- **AC 2.1.2 Quyền truy cập tài liệu đính kèm:**

  - Cuộc họp có đính kèm file (PDF, DOCX) và được đánh dấu mức độ Nội Bộ hoặc Bí Mật.

  - Người dùng truy cập link tải file.

  - Hệ thống kiểm tra: Tài khoản đã đăng nhập + Có nằm trong danh sách Mời họp.

  - Nếu không đủ điều kiện, trả về mã lỗi 403 Forbidden và chặn không cho xem/tải.

### **MODULE 3: HIỂN THỊ, TRUYỀN THÔNG VÀ TÍCH HỢP HẠ TẦNG.**

#### **US-ICTU-04: Tự động xuất Lịch tuần công tác và đẩy dữ liệu ra Bảng điện tử.** 

- **Tư cách:** Chuyên viên Văn phòng Trường.

<!-- -->

- **Muốn:** Tự động hóa việc tổng hợp Lịch tuần và hiển thị lên các màn hình công cộng.

- **Kết quả:** Tiết kiệm thời gian nhập liệu thủ công và tăng tính chuyên nghiệp.

- **AC 3.1.1 Xuất file Lịch tuần chuẩn hành chính:**

  - Danh sách các cuộc họp Cấp Trường đã được phê duyệt trong tuần.

  - Chọn chức năng "Xuất Lịch tuần".

  - Hệ thống xuất ra file PDF/Word đúng mẫu văn bản hành chính của Trường ICTU bao gồm: Bìa, Thứ/Ngày, Thời gian, Nội dung, Thành phần, Chủ trì, Địa điểm.

- **AC 3.1.2 Đồng bộ lịch họp:**

  - Hệ thống trả về dữ liệu JSON gồm các cuộc họp trong ngày.

  - Giao diện màn hình tự động cập nhật:

    - Báo **Đang họp (Màu đỏ)** nếu start_time \<= Current_time \<= end_time.

    - Báo **Sắp diễn ra (Màu vàng)** nếu trước start_time 30 phút.

    - Báo **Phòng trống (Màu xanh)** khi không có lịch.

**III. YÊU CẦU PHI CHỨC NĂNG.**

### **1. Tốc độ & Khả năng chịu tải (Hiệu năng phần mềm).**

*Hệ thống phải chạy mượt, phản hồi nhanh và không bị giật lag khi có nhiều người truy cập cùng lúc.*

- **Mở lịch:**

  - Khi bấm xem Lịch tuần toàn trường hay bấm đổi giữa các ngày/tháng, màn hình phải hiển thị xong trong **dưới 1 giây**.

- **Kiểm tra trùng lịch dạy:**

  - Khi bấm kiểm tra xem Giảng viên có bị vướng Thời khóa biểu (TKB) trên lớp hay không, hệ thống phải trả về kết quả trong **chưa tới 1 giây**.

- **Gánh tải ngày cao điểm:**

  - Vào tầm **07:00 – 08:00 sáng Thứ Hai hàng tuần** (thời điểm cả trường cùng vào xem lịch công tác), hệ thống phải chịu được cùng lúc **ít nhất 5.000 người truy cập** mà không bị sập hay quay vòng vòng.

### **2. Độ an toàn & Bảo mật thông tin.**

*Đúng người đúng việc, tài liệu họp mật không bị lộ ra ngoài.*

- **Đăng nhập 1 tài khoản duy nhất:**

  - Thầy cô và sinh viên dùng chính tài khoản Email trường cấp ([**@ictu.edu.vn**](mailto:@ictu.edu.vn)) để đăng nhập, không cần tạo tài khoản mới.

- **Ai được mời mới xem được file:**

  - Với các cuộc họp Hội đồng hay họp BGH có file đính kèm nhãn **"Mật"**, chỉ những ai có tên trong danh sách mời mới tải/xem được file. Người ngoài bấm vào link sẽ bị báo lỗi "Không có quyền truy cập".

- **Bảo vệ dữ liệu:**

  - Mọi dữ liệu truyền đi trên trang web đều được mã hóa (khóa bảo mật) để tránh bị hacker đánh cắp thông tin cuộc họp.

### **3. Độ tin cậy & Sẵn sàng phục vụ.**

*Hệ thống luôn luôn hoạt động, hiếm khi bị lỗi và nếu có sự cố thì khôi phục rất nhanh.*

- **Hoạt động liên tục 24/7:**

  - Hệ thống cam kết chạy ổn định **99.9% thời gian trong năm** (chỉ cho phép ngừng hệ thống tối đa vài tiếng một năm để bảo trì, và phải làm vào ban đêm/cuối tuần).

- **Cứu dữ liệu khi gặp sự cố:**

  - Dữ liệu lịch họp được **tự động lưu dự phòng (Backup) hàng ngày**. Nếu máy chủ gặp sự cố cháy nổ/mất điện, kỹ thuật viên có thể khôi phục lại dữ liệu trong vòng **dưới 1 giờ** và không bị mất quá 15 phút dữ liệu gần nhất.

### **4. Khả năng kết nối & Tích hợp thiết bị.**

*Hệ thống phải "nói chuyện" được với các phần mềm và thiết bị công nghệ khác trong trường.*

- **Tự tạo link họp Online:**

  - Khi chọn họp Online qua Microsoft Teams hay Zoom, hệ thống tự động sinh ra link họp và dán vào lịch, không bắt thầy cô phải mở phần mềm Teams ra tạo tay.

- **Thông báo nhắc lịch:**

  - Tự động gửi tin nhắn nhắc họp qua Email trường hoặc Zalo trước giờ họp 30 phút.

- **Đồng bộ lịch họp:**

  - Màn hình hiện **Màu đỏ**: Phòng đang họp.

  - Màn hình hiện **Màu xanh**: Phòng đang trống.

### **5. Dễ sử dụng & Thân thiện người dùng.**

*Mọi người xem là hiểu ngay, không mất thời gian học cách dùng.*

- **Thao tác đơn giản:** Thầy cô chỉ mất tối đa **3 cú nhấp chuột** là tạo xong 1 lịch họp cơ bản.

- **Tự điều chỉnh giao diện:** Mở trên máy tính, máy tính bảng hay điện thoại di động thì giao diện đều tự căn chỉnh đẹp mắt, dễ đọc.

- **Xuất file in ấn ngay:** Văn phòng Trường chỉ cần bấm 1 nút là tải được file Lịch tuần (PDF/Word) đóng dấu theo đúng mẫu văn bản hành chính của Trường ICTU để dán bảng tin hoặc gửi Ban Giám hiệu.
