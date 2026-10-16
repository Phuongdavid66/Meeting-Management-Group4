# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

React + Vite, kết nối Backend Python FastAPI (REST API /api/v1)

## Users

- **Giảng viên / Cán bộ chủ trì (Organizer):** Cần lên lịch họp khoa/bộ môn, tìm kiếm phòng họp khả dụng theo sức chứa và vị trí, đặt thiết bị kèm theo (máy chiếu, micro), gửi lời mời tự động tới đồng nghiệp.
- **Sinh viên / Người tham gia (Participant):** Nhận thông báo mời họp, xem lịch họp cá nhân, phản hồi xác nhận tham gia (Accept/Decline) và quét mã QR check-in điểm danh khi vào phòng.
- **Quản trị viên (Admin):** Quản lý tài khoản người dùng, phòng ban, danh mục phòng họp vật lý, cấu hình giới hạn quyền đặt phòng theo vai trò (US #21), theo dõi báo cáo thống kê sử dụng tài nguyên.

## Product Purpose

Hệ thống Quản lý Lịch họp và Phòng họp cho Trường Đại học Công nghệ Thông tin & Truyền thông (ICTU) nhằm số hóa và tự động hóa toàn bộ quy trình đặt phòng, ngăn chặn hoàn toàn tình trạng trùng lịch (conflict detection), quản lý thiết bị mượn kèm, điểm danh bằng mã QR và cung cấp báo cáo thống kê phục vụ công tác điều hành của nhà trường.

## Positioning

Hệ thống đặt lịch chuyên biệt cho môi trường giáo dục đại học với cơ chế phân quyền đặt phòng chặt chẽ theo vai trò (Role-based Room Restriction), phát hiện trùng lịch tức thời (Real-time Conflict Detection), và hỗ trợ điểm danh nhanh bằng mã QR tại cửa phòng họp.

## Operating Context

- Trình duyệt Web trên máy tính (Desktop/Laptop) phục vụ công tác quản trị, duyệt phòng và lên lịch chi tiết.
- Trình duyệt Web trên thiết bị di động (Mobile Responsive) phục vụ việc tra cứu lịch cá nhân và quét mã QR check-in khi vào phòng họp.
- Tích hợp mạng nội bộ và hệ sinh thái tài khoản của trường ICTU.

## Capabilities and Constraints

- **Kiến trúc:** Client-Server tách biệt.
  - Backend: Python 3.11, FastAPI, SQLAlchemy 2.0, SQLite (local dev `meetings.db`) / PostgreSQL, JWT Authentication. Đã hoàn thành Giai đoạn 1 (Auth & RBAC) và Giai đoạn 2 (Room Management & Restrictions).
  - Frontend: React + Vite, Single Page Application.
- **Quy tắc cốt lõi (Hard Constraints):**
  - Chống trùng lịch tuyệt đối: Không cho phép 2 cuộc họp đặt cùng 1 phòng trong cùng khung thời gian.
  - Phân quyền đặt phòng (US #21): Tự động kiểm tra và ngăn chặn người dùng đặt các phòng bị giới hạn đối với vai trò của họ (ví dụ: sinh viên không được tự đặt phòng Ban Giám hiệu).

## Brand Commitments

- **Đơn vị chủ quản:** Trường Đại học Công nghệ Thông tin & Truyền thông — Đại học Thái Nguyên (ICTU).
- **Tone & Mood:** Công nghệ, chuyên nghiệp, hiện đại, thanh lịch, đáng tin cậy.
- **Màu sắc chủ đạo:** Xanh công nghệ (Tech Blue / Deep Navy), kết hợp màu trắng tinh tế và xám slate hiện đại.

## Evidence on Hand

- Tài liệu Product Backlog: [`backlog_analysis.md`](backlog_analysis.md) (28 User Stories / 7 Epics).
- Sơ đồ cơ sở dữ liệu hoàn chỉnh: [`database.drawio`](database.drawio) (10 Entities).
- Bản kế hoạch phân rã 8 giai đoạn: [`development_roadmap.md`](development_roadmap.md).
- Backend APIs đã triển khai và pass 100% tests: [`test_phase1.py`](backend/test_phase1.py) (9/9 passed) và [`test_phase2.py`](backend/test_phase2.py) (11/11 passed).

## Product Principles

1. **Rõ ràng & Không xung đột (Conflict-Free First):** Mọi thao tác đặt phòng phải minh bạch về trạng thái thời gian thực, không bao giờ để xảy ra đặt trùng giờ.
2. **Nhanh chóng & Trực quan (Frictionless Scheduling):** Người dùng tìm phòng và đặt lịch chỉ trong vòng 3 thao tác cơ bản.
3. **Phân quyền chính xác (Right Access, Right Space):** Đảm bảo đúng đối tượng được phép sử dụng đúng phòng họp theo quy chế của nhà trường.
4. **Trải nghiệm nhất quán (Responsive & Seamless):** Thao tác mượt mà trên cả desktop của giảng viên và điện thoại của sinh viên.
