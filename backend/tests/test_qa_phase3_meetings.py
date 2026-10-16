"""
QA Test Suite - Phase 3: Core Booking, Conflict Detection & Meeting Life Cycle
Kiểm thử chuyên sâu các lỗ hổng logic nghiệp vụ đặt lịch, chống trùng lặp và phân quyền phòng.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.db.init_db import init_db
from app.models.meeting import Meeting, MeetingParticipant
from app.models.room import Room

@pytest.fixture(scope="module")
def client():
    db = SessionLocal()
    init_db(db)
    from app.models.meeting import Meeting, MeetingParticipant
    db.query(MeetingParticipant).delete()
    db.query(Meeting).delete()
    db.commit()
    db.close()
    return TestClient(app)

@pytest.fixture(scope="module")
def admin_headers(client):
    res = client.post("/api/v1/auth/login", json={"email": "admin@ictu.vn", "password": "Admin@123"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

@pytest.fixture(scope="module")
def organizer_headers(client):
    res = client.post("/api/v1/auth/login", json={"email": "organizer@ictu.vn", "password": "123456"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

@pytest.fixture(scope="module")
def participant_headers(client, admin_headers):
    res = client.get("/api/v1/users?search=student1@ictu.vn", headers=admin_headers)
    if not res.json():
        client.post("/api/v1/users", json={
            "email": "student1@ictu.vn",
            "password": "password123",
            "full_name": "Nguyen Van Sinh Vien",
            "role_id": 3,
            "status": "ACTIVE"
        }, headers=admin_headers)
    res_login = client.post("/api/v1/auth/login", json={"email": "student1@ictu.vn", "password": "password123"})
    return {"Authorization": f"Bearer {res_login.json()['access_token']}"}


def test_booking_maintenance_room_should_fail(client, organizer_headers):
    """Đặt phòng đang có trạng thái MAINTENANCE -> Phải bị chặn 400 Bad Request"""
    # Lấy phòng đang bảo trì
    rooms = client.get("/api/v1/rooms?status=MAINTENANCE", headers=organizer_headers).json()
    assert len(rooms) > 0, "Cần có ít nhất 1 phòng bảo trì trong seed data"
    maint_room_id = rooms[0]["room_id"]

    tomorrow = datetime.now() + timedelta(days=3)
    res = client.post("/api/v1/meetings", json={
        "room_id": maint_room_id,
        "title": "Họp phòng bảo trì",
        "start_time": tomorrow.replace(hour=10, minute=0, second=0).isoformat(),
        "end_time": tomorrow.replace(hour=11, minute=0, second=0).isoformat()
    }, headers=organizer_headers)

    assert res.status_code == 400
    assert "bảo trì" in res.json()["detail"].lower()


def test_booking_with_invalid_time_range(client, organizer_headers):
    """Đặt lịch với start_time >= end_time -> Phải bị chặn 400"""
    rooms = client.get("/api/v1/rooms?status=AVAILABLE", headers=organizer_headers).json()
    room_id = rooms[0]["room_id"]

    tomorrow = datetime.now() + timedelta(days=3)
    # start_time sau end_time
    res = client.post("/api/v1/meetings", json={
        "room_id": room_id,
        "title": "Họp ngược thời gian",
        "start_time": tomorrow.replace(hour=14, minute=0, second=0).isoformat(),
        "end_time": tomorrow.replace(hour=13, minute=0, second=0).isoformat()
    }, headers=organizer_headers)

    assert res.status_code == 400


def test_critical_bug_room_restriction_inversion(client, organizer_headers, participant_headers):
    """
    KIỂM THỬ LỖI NGHIỆP VỤ NGHIÊM TRỌNG (CRITICAL LOGIC FLAW):
    Phòng Ban Giám hiệu (A1-201) được cấu hình giới hạn (RoomRestriction) cấm Sinh viên (Role: PARTICIPANT = 3) đặt.
    Kỳ vọng:
      1. Giảng viên (ORGANIZER = 2) được phép đặt phòng Ban Giám hiệu.
      2. Sinh viên (PARTICIPANT = 3) bị cấm đặt phòng Ban Giám hiệu (403 Forbidden).
    Thực tế trong code meetings.py:
      meetings.py coi RoomRestriction là WHITELIST (allowed_roles = [r.role_id for r in restrictions]).
      Dẫn tới: Giảng viên bị chặn (403), trong khi Sinh viên lại được phép đặt!
    """
    # Tìm phòng Ban Giám hiệu
    bgh_rooms = client.get("/api/v1/rooms?search=Ban%20Gi%C3%A1m%20hi%E1%BB%87u", headers=organizer_headers).json()
    assert len(bgh_rooms) > 0, "Không tìm thấy phòng Ban Giám hiệu trong hệ thống"
    bgh_room_id = bgh_rooms[0]["room_id"]

    tomorrow = datetime.now() + timedelta(days=5)
    booking_payload = {
        "room_id": bgh_room_id,
        "title": "Cuộc họp Kiểm thử Quyền VIP",
        "start_time": tomorrow.replace(hour=8, minute=30, second=0).isoformat(),
        "end_time": tomorrow.replace(hour=10, minute=30, second=0).isoformat()
    }

    # 1. Giảng viên (Organizer) đặt phòng
    res_org = client.post("/api/v1/meetings", json=booking_payload, headers=organizer_headers)
    
    # 2. Sinh viên (Participant) đặt phòng
    res_part = client.post("/api/v1/meetings", json=booking_payload, headers=participant_headers)

    # Phát hiện lỗi đảo ngược logic
    if res_org.status_code == 403 and res_part.status_code == 201:
        pytest.fail(
            "CRITICAL LOGIC INVERSION BUG in meetings.py! "
            "RoomRestriction was treated as WHITELIST instead of BLACKLIST: "
            "Organizer (Lecturer) was BLOCKED (403) from BGH room, while Student (Participant) was ALLOWED (201)!"
        )


def test_critical_bug_conflict_detection_bypass_on_partial_update(client, organizer_headers):
    """
    KIỂM THỬ LỖ HỔNG XUNG ĐỘT (CONFLICT DETECTION BYPASS ON PARTIAL UPDATE):
    Trong meetings.py, điều kiện kiểm tra conflict tại update_meeting là:
      `if data.start_time and data.end_time:`
    Nếu người dùng chỉ cập nhật `start_time` (hoặc chỉ `end_time`, hoặc chỉ `room_id`),
    điều kiện này bị bỏ qua HOÀN TOÀN -> Gây đè lịch/trùng lịch (Double Booking)!
    """
    rooms = client.get("/api/v1/rooms?status=AVAILABLE", headers=organizer_headers).json()
    # Chọn phòng thông thường không có restriction
    room_id = [r["room_id"] for r in rooms if "Ban Giám hiệu" not in r["room_name"]][0]

    day = datetime.now() + timedelta(days=6)
    
    # Tạo Meeting A: 09:00 - 11:00
    res_a = client.post("/api/v1/meetings", json={
        "room_id": room_id,
        "title": "Meeting A (Gốc)",
        "start_time": day.replace(hour=9, minute=0, second=0).isoformat(),
        "end_time": day.replace(hour=11, minute=0, second=0).isoformat()
    }, headers=organizer_headers)
    assert res_a.status_code == 201, res_a.text
    meeting_a_id = res_a.json()["meeting_id"]

    # Tạo Meeting B: 14:00 - 16:00
    res_b = client.post("/api/v1/meetings", json={
        "room_id": room_id,
        "title": "Meeting B",
        "start_time": day.replace(hour=14, minute=0, second=0).isoformat(),
        "end_time": day.replace(hour=16, minute=0, second=0).isoformat()
    }, headers=organizer_headers)
    assert res_b.status_code == 201, res_b.text
    meeting_b_id = res_b.json()["meeting_id"]

    # Thử sửa Meeting B: Chỉ truyền start_time = 09:30 (nằm trọn trong Meeting A 09:00-11:00)
    # Không truyền end_time
    patch_res = client.put(f"/api/v1/meetings/{meeting_b_id}", json={
        "start_time": day.replace(hour=9, minute=30, second=0).isoformat()
    }, headers=organizer_headers)

    # Nếu hệ thống cho phép sửa thành công (200) thay vì chặn 409 hoặc 400:
    if patch_res.status_code == 200:
        pytest.fail(
            "CRITICAL BUG DETECTED: Partial update of start_time without end_time bypassed conflict detection! "
            "Two overlapping meetings now exist at the same room and time!"
        )


def test_bug_update_meeting_to_maintenance_or_invalid_room(client, organizer_headers):
    """
    KIỂM THỬ LỖ HỔNG: update_meeting cho phép chuyển meeting sang phòng bảo trì hoặc phòng không tồn tại.
    """
    rooms = client.get("/api/v1/rooms?status=AVAILABLE", headers=organizer_headers).json()
    avail_room_id = [r["room_id"] for r in rooms if "Ban Giám hiệu" not in r["room_name"]][0]

    maint_rooms = client.get("/api/v1/rooms?status=MAINTENANCE", headers=organizer_headers).json()
    maint_room_id = maint_rooms[0]["room_id"]

    day = datetime.now() + timedelta(days=7)
    create_res = client.post("/api/v1/meetings", json={
        "room_id": avail_room_id,
        "title": "Meeting chuyển sang phòng hỏng",
        "start_time": day.replace(hour=13, minute=0, second=0).isoformat(),
        "end_time": day.replace(hour=14, minute=0, second=0).isoformat()
    }, headers=organizer_headers)
    meeting_id = create_res.json()["meeting_id"]

    # Sửa room_id sang phòng đang bảo trì
    upd_res = client.put(f"/api/v1/meetings/{meeting_id}", json={
        "room_id": maint_room_id
    }, headers=organizer_headers)

    if upd_res.status_code == 200:
        pytest.fail("VALIDATION BUG: Meeting room can be updated to a MAINTENANCE room without validation check!")


def test_bug_respond_to_cancelled_meeting(client, organizer_headers, participant_headers):
    """
    KIỂM THỬ NGHIỆP VỤ: Người tham gia vẫn có thể phản hồi ACCEPTED vào một cuộc họp ĐÃ BỊ HỦY (CANCELLED).
    """
    rooms = client.get("/api/v1/rooms?status=AVAILABLE", headers=organizer_headers).json()
    room_id = [r["room_id"] for r in rooms if "Ban Giám hiệu" not in r["room_name"]][0]

    # Lấy ID của participant
    part_me = client.get("/api/v1/auth/me", headers=participant_headers).json()
    part_id = part_me["user_id"]

    day = datetime.now() + timedelta(days=8)
    create_res = client.post("/api/v1/meetings", json={
        "room_id": room_id,
        "title": "Meeting sắp bị hủy",
        "start_time": day.replace(hour=15, minute=0, second=0).isoformat(),
        "end_time": day.replace(hour=16, minute=0, second=0).isoformat(),
        "participant_ids": [part_id]
    }, headers=organizer_headers)
    meeting_id = create_res.json()["meeting_id"]

    # Organizer hủy cuộc họp
    cancel_res = client.patch(f"/api/v1/meetings/{meeting_id}/cancel", headers=organizer_headers)
    assert cancel_res.status_code == 200

    # Participant cố phản hồi ACCEPTED vào cuộc họp đã bị hủy
    resp_res = client.patch(f"/api/v1/meetings/{meeting_id}/respond", json={"status": "ACCEPTED"}, headers=participant_headers)

    if resp_res.status_code == 200:
        pytest.fail("LOGIC BUG: User is allowed to respond 'ACCEPTED' to a CANCELLED meeting!")
