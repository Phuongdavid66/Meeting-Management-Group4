# 📋 BÁO CÁO KIỂM THỬ VÀ PHÁT HIỆN LỖI (QA BUG REPORT)
**Dự án:** Hệ Thống Quản Lý Lịch Họp (Meeting Management System - ICTU)  
**Phân hệ kiểm thử:** Backend API (Phase 1, Phase 2, Phase 3)  
**Vai trò thực hiện:** QA Agent (Chỉ tìm lỗi, viết test, chạy test, không sửa code ứng dụng)  
**Ngày lập báo cáo:** 2026-10-16  
**Công cụ kiểm thử tự động:** `pytest 9.1.1`, `fastapi.testclient`, Python 3.14  
**Kịch bản test thực thi:** `backend/tests/test_qa_phase1_auth.py`, `backend/tests/test_qa_phase2_rooms.py`, `backend/tests/test_qa_phase3_meetings.py`, `backend/run_qa_tests.py`

---

## 🎯 1. TỔNG QUAN KẾT QUẢ KIỂM THỬ

| Module / Phân hệ | Tổng số Test Cases | Số Test Đạt (Pass) | Số Bug Phát Hiện (Fail) | Mức độ nghiêm trọng cao nhất |
| :--- | :---: | :---: | :---: | :---: |
| **Phase 1: Auth & User Management** | 8 | 6 | **2** | 🔴 HIGH (Lỗ hổng bảo mật) |
| **Phase 2: Room Management & Restrictions** | 5 | 3 | **2** | 🟡 MEDIUM (Toàn vẹn dữ liệu) |
| **Phase 3: Core Booking & Life Cycle** | 6 | 2 | **4** | 🔴 CRITICAL (Lỗi đảo ngược logic & Double booking) |
| **TỔNG CỘNG** | **19** | **11** | **8 BUGS** | **🔴 CRITICAL** |

---

## 🚨 2. DANH SÁCH CHI TIẾT CÁC LỖI (BUG DETAILS)

---

### 🔴 BUG-01 [CRITICAL]: Đảo ngược logic kiểm tra quyền đặt phòng (Room Restriction Inversion)
- **Vị trí code:** [`backend/app/api/v1/endpoints/meetings.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/app/api/v1/endpoints/meetings.py#L32-L38)
- **Mức độ:** 🔴 **CRITICAL** (Sai lệch hoàn toàn phân quyền nghiệp vụ)
- **File Test tái hiện:** [`backend/tests/test_qa_phase3_meetings.py::test_critical_bug_room_restriction_inversion`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase3_meetings.py)
- **Mô tả chi tiết:**
  - Trong model và seed data, bảng `room_restrictions` đóng vai trò là **Danh sách đen (Blacklist)**: nếu 1 vai trò xuất hiện trong `room_restrictions` của phòng, vai trò đó **bị cấm** đặt phòng (Ví dụ: Phòng Ban Giám hiệu cấm `PARTICIPANT` - Sinh viên đặt).
  - Tuy nhiên, tại `meetings.py` (hàm `create_meeting`), code lại coi đây là **Danh sách trắng (Whitelist)**:
    ```python
    restrictions = db.query(RoomRestriction).filter(RoomRestriction.room_id == data.room_id).all()
    if restrictions:
        allowed_roles = [r.role_id for r in restrictions]
        if current_user.role_id not in allowed_roles:
            raise HTTPException(status_code=403, detail="Bạn không có quyền đặt phòng này")
    ```
- **Hậu quả:**
  - **Giảng viên (ORGANIZER)** bị hệ thống chặn với mã lỗi `403 Forbidden` khi đặt phòng Ban Giám hiệu!
  - **Sinh viên (PARTICIPANT)** - đối tượng vốn bị cấm - lại được hệ thống cho phép đặt phòng Ban Giám hiệu thành công (`201 Created`)!
- **Khuyến nghị cho Coding Agent:**
  - Đổi biến và logic kiểm tra thành Blacklist:
    ```python
    restricted_role_ids = [r.role_id for r in restrictions]
    if current_user.role_id in restricted_role_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vai trò của bạn không được phép đặt phòng này")
    ```

---

### 🔴 BUG-02 [CRITICAL]: Vượt mặt thuật toán chống trùng lịch khi cập nhật từng phần (Conflict Detection Bypass on Partial Update)
- **Vị trí code:** [`backend/app/api/v1/endpoints/meetings.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/app/api/v1/endpoints/meetings.py#L121-L135)
- **Mức độ:** 🔴 **CRITICAL** (Dẫn tới trùng lịch họp - Double Booking)
- **File Test tái hiện:** [`backend/tests/test_qa_phase3_meetings.py::test_critical_bug_conflict_detection_bypass_on_partial_update`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase3_meetings.py)
- **Mô tả chi tiết:**
  - Khi gọi `PUT /api/v1/meetings/{meeting_id}`, hệ thống chỉ kiểm tra xung đột thời gian nếu client gửi đồng thời cả `start_time` VÀ `end_time`:
    ```python
    if data.start_time and data.end_time:
        # kiểm tra conflict
    ```
  - Nếu người dùng chỉ gửi `{ "start_time": "..." }` hoặc chỉ `{ "end_time": "..." }` hoặc chỉ `{ "room_id": "..." }`, toàn bộ khối kiểm tra xung đột bị bỏ qua!
  - Sau đó, ở các dòng 139-140, giá trị mới vẫn được gán trực tiếp vào meeting (`meeting.start_time = data.start_time`).
- **Hậu quả:**
  - Người tổ chức có thể sửa giờ bắt đầu của một cuộc họp đè vào giờ của một cuộc họp khác đã có sẵn trong phòng mà API không hề trả về `409 Conflict`.
  - Có thể dẫn tới tình huống `start_time > end_time` nếu chỉ cập nhật 1 trường.
  - Người dùng có thể đổi phòng (`room_id`) sang một phòng đang có lịch kín mà không bị kiểm tra xung đột với phòng mới.
- **Khuyến nghị cho Coding Agent:**
  - Lấy thời gian hiệu lực: `new_start = data.start_time or meeting.start_time` và `new_end = data.end_time or meeting.end_time`, `new_room_id = data.room_id or meeting.room_id`.
  - Luôn kiểm tra `new_start < new_end` và chạy truy vấn kiểm tra trùng lịch với `new_start`, `new_end`, `new_room_id` bất kể người dùng cập nhật 1 hay nhiều trường.

---

### 🔴 BUG-03 [HIGH]: Bỏ qua xác thực mật khẩu cũ và độ dài tối thiểu qua API cập nhật thông tin cá nhân
- **Vị trí code:** [`backend/app/api/v1/endpoints/users.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/app/api/v1/endpoints/users.py#L131-L133)
- **Mức độ:** 🔴 **HIGH** (Lỗ hổng an ninh xác thực)
- **File Test tái hiện:** [`backend/tests/test_qa_phase1_auth.py::test_security_flaw_password_bypass_via_update_user`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase1_auth.py)
- **Mô tả chi tiết:**
  - Trong khi endpoint `POST /api/v1/auth/change-password` bắt buộc phải nhập `old_password` và kiểm tra `len(new_password) >= 6`, endpoint `PUT /api/v1/users/{user_id}` lại cho phép người dùng truyền thẳng trường `password` trong payload.
  - Đoạn code xử lý:
    ```python
    if data.password:
        user.password_hash = get_password_hash(data.password)
    ```
- **Hậu quả:**
  - Bất kỳ người dùng nào cũng có thể đổi mật khẩu mà không cần cung cấp mật khẩu cũ (rủi ro nghiêm trọng khi tài khoản bị chiếm session hoặc CSRF).
  - Có thể đặt mật khẩu chỉ có 1 ký tự (ví dụ `"1"`), vi phạm chính sách bảo mật mật khẩu.
- **Khuyến nghị cho Coding Agent:**
  - Chỉ cho phép Admin đổi mật khẩu trực tiếp cho người khác qua `update_user` (nếu là tính năng Reset password của Admin), hoặc loại bỏ trường `password` ra khỏi `UserUpdate` và yêu cầu mọi thay đổi mật khẩu phải qua luồng `POST /api/v1/auth/change-password`.

---

### 🔴 BUG-04 [HIGH]: Cập nhật cuộc họp sang phòng đang bảo trì hoặc phòng không tồn tại
- **Vị trí code:** [`backend/app/api/v1/endpoints/meetings.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/app/api/v1/endpoints/meetings.py#L136)
- **Mức độ:** 🔴 **HIGH** (Lỗi nghiệp vụ & Tính toàn vẹn dữ liệu)
- **File Test tái hiện:** [`backend/tests/test_qa_phase3_meetings.py::test_bug_update_meeting_to_maintenance_or_invalid_room`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase3_meetings.py)
- **Mô tả chi tiết:**
  - Tại `create_meeting`, hệ thống có kiểm tra `room.status != "AVAILABLE"` và quyền phòng.
  - Tuy nhiên tại `update_meeting`, nếu truyền `data.room_id`, hệ thống gán trực tiếp:
    ```python
    if data.room_id is not None: meeting.room_id = data.room_id
    ```
  - Hoàn toàn KHÔNG kiểm tra xem `data.room_id` có tồn tại trong CSDL hay không, có đang bị `MAINTENANCE` hay không, và vai trò người dùng có bị cấm đặt phòng đó hay không!
- **Hậu quả:**
  - Cuộc họp có thể bị chuyển vào phòng đang hỏng hóc/sửa chữa hoặc phòng có ID không tồn tại (gây lỗi khóa ngoại).
- **Khuyến nghị cho Coding Agent:**
  - Thêm bước truy vấn và kiểm tra `Room` khi `data.room_id is not None` tương tự như hàm `create_meeting`.

---

### 🟡 BUG-05 [MEDIUM]: Cho phép phản hồi tham gia vào cuộc họp đã bị hủy (CANCELLED)
- **Vị trí code:** [`backend/app/api/v1/endpoints/meetings.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/app/api/v1/endpoints/meetings.py#L163-L184)
- **Mức độ:** 🟡 **MEDIUM** (Lỗi logic trạng thái cuộc họp)
- **File Test tái hiện:** [`backend/tests/test_qa_phase3_meetings.py::test_bug_respond_to_cancelled_meeting`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase3_meetings.py)
- **Mô tả chi tiết:**
  - Khi gọi `PATCH /api/v1/meetings/{meeting_id}/respond`, hệ thống chỉ kiểm tra `MeetingParticipant` mà không kiểm tra trạng thái của cuộc họp `meeting.status`.
- **Hậu quả:**
  - Người tham gia vẫn có thể gửi phản hồi `ACCEPTED` hoặc `DECLINED` vào một cuộc họp đã bị hủy bỏ từ trước.
- **Khuyến nghị cho Coding Agent:**
  - Thêm kiểm tra:
    ```python
    meeting = db.query(Meeting).filter(Meeting.meeting_id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch họp")
    if meeting.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Cuộc họp này đã bị hủy, không thể phản hồi")
    ```

---

### 🟡 BUG-06 [MEDIUM]: API xem availability phòng không tồn tại trả về 200 OK thay vì 404 Not Found
- **Vị trí code:** [`backend/app/api/v1/endpoints/rooms.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/app/api/v1/endpoints/rooms.py#L145-L163)
- **Mức độ:** 🟡 **MEDIUM** (Sai lệch chuẩn RESTful API)
- **File Test tái hiện:** [`backend/tests/test_qa_phase2_rooms.py::test_bug_availability_on_nonexistent_room`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase2_rooms.py)
- **Mô tả chi tiết:**
  - Endpoint `GET /api/v1/rooms/{room_id}/availability` không kiểm tra `room_id` có tồn tại trong CSDL hay không trước khi query meeting.
  - Khi truyền `room_id = 99999`, hệ thống trả về mã `200 OK` với mảng rỗng `[]`.
- **Hậu quả:**
  - Phía Frontend sẽ hiểu lầm rằng phòng `99999` là phòng hợp lệ và đang trống cả ngày, cho phép người dùng tiếp tục thao tác đặt phòng vào một phòng không có thực.
- **Khuyến nghị cho Coding Agent:**
  - Kiểm tra `room = db.query(Room).filter(Room.room_id == room_id).first()`. Nếu `None`, trả về `404 Not Found`.

---

### 🟡 BUG-07 [MEDIUM]: Thiếu cơ chế xử lý các cuộc họp liên kết khi xóa phòng họp (Data Integrity Risk)
- **Vị trí code:** [`backend/app/api/v1/endpoints/rooms.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/app/api/v1/endpoints/rooms.py#L130-L141)
- **Mức độ:** 🟡 **MEDIUM** (Rủi ro tính toàn vẹn CSDL)
- **File Test tái hiện:** [`backend/tests/test_qa_phase2_rooms.py::test_bug_delete_room_with_active_meetings`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase2_rooms.py)
- **Mô tả chi tiết:**
  - `delete_room` trực tiếp gọi `db.delete(room)` mà không kiểm tra xem phòng có các cuộc họp trong tương lai (`SCHEDULED`) hay không.
  - Trên CSDL SQLite mặc định nếu không bật Foreign Key constraint, meeting sẽ bị mồ côi (orphaned record với `room_id` không tồn tại). Nếu trên PostgreSQL có khóa ngoại, API sẽ văng `IntegrityError` và sập với mã lỗi 500.
- **Khuyến nghị cho Coding Agent:**
  - Kiểm tra: nếu phòng đang có cuộc họp `SCHEDULED` chưa diễn ra, chặn không cho xóa (trả về 400 Bad Request kèm thông báo cần dời lịch hoặc hủy các cuộc họp trước).

---

### 🟡 BUG-08 [LOW/MEDIUM]: Rủi ro Admin tự vô hiệu hóa tài khoản của chính mình (Self-Lockout Risk)
- **Vị trí code:** [`backend/app/api/v1/endpoints/users.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/app/api/v1/endpoints/users.py#L138-L151)
- **Mức độ:** 🟡 **LOW/MEDIUM** (Rủi ro vận hành)
- **File Test tái hiện:** [`backend/tests/test_qa_phase1_auth.py::test_admin_self_deactivation_risk`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase1_auth.py)
- **Mô tả chi tiết:**
  - `DELETE /api/v1/users/{user_id}` cho phép Admin đang đăng nhập tự vô hiệu hóa tài khoản của chính họ (`current_user.user_id == user_id`).
  - Nếu hệ thống chỉ có một tài khoản Admin duy nhất, hành động này sẽ khóa vĩnh viễn quyền quản trị của toàn hệ thống.
- **Khuyến nghị cho Coding Agent:**
  - Thêm điều kiện: `if _current_user.user_id == user_id: raise HTTPException(status_code=400, detail="Không thể tự vô hiệu hóa tài khoản quản trị đang đăng nhập")`.

---

## 🛠️ 3. TÀI LIỆU VÀ CÔNG CỤ ĐÃ THIẾT LẬP CHO BƯỚC TIẾP THEO

QA Agent đã tạo sẵn toàn bộ các kịch bản test tự động và runner script để **Coding Agent** có thể sử dụng ngay lập tức khi thực hiện sửa lỗi:

1. **Test Suites:**
   - [`backend/tests/test_qa_phase1_auth.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase1_auth.py)
   - [`backend/tests/test_qa_phase2_rooms.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase2_rooms.py)
   - [`backend/tests/test_qa_phase3_meetings.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/tests/test_qa_phase3_meetings.py)
2. **Runner Script:**
   - [`backend/run_qa_tests.py`](file:///c:/Users/phuong/Desktop/Meeting-Management-Group4-main%20%281%29/Meeting-Management-Group4-main/backend/run_qa_tests.py) (Chạy toàn bộ test suites và báo cáo trạng thái).
3. **Môi trường:**
   - Đã cấu hình và kiểm thử thành công trên môi trường Virtualenv Python 3.14 (`backend/.venv`).

> **Ghi chú quan trọng:** QA Agent **KHÔNG THỰC HIỆN BẤT KỲ THAY ĐỔI NÀO** trên code ứng dụng (`backend/app/`). Toàn bộ mã nguồn backend vẫn được giữ nguyên vẹn 100% để chuyển giao sang **Coding Agent**.
