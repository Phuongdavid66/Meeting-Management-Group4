"""
QA Test Suite - Phase 2: Room Management & Role-Based Restrictions
Kiểm thử các kịch bản CRUD phòng, phân quyền Admin, tính toàn vẹn dữ liệu và kiểm tra lịch phòng.
"""
import pytest
from datetime import datetime, timedelta, date
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.db.init_db import init_db
from app.models.room import Room
from app.models.meeting import Meeting

@pytest.fixture(scope="module")
def client():
    db = SessionLocal()
    init_db(db)
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


def test_non_admin_cannot_create_or_modify_rooms(client, organizer_headers, participant_headers):
    """Người dùng không phải Admin không được phép tạo, sửa hoặc xóa phòng (Phải 403)"""
    room_payload = {
        "room_name": "Unauthorized Room Test",
        "capacity": 20,
        "location": "Tòa A",
        "status": "AVAILABLE"
    }
    # 1. Organizer cố tạo phòng -> 403
    res1 = client.post("/api/v1/rooms", json=room_payload, headers=organizer_headers)
    assert res1.status_code == 403

    # 2. Participant cố xóa phòng 1 -> 403
    res2 = client.delete("/api/v1/rooms/1", headers=participant_headers)
    assert res2.status_code == 403

    # 3. Organizer cố cấu hình restriction -> 403
    res3 = client.post("/api/v1/rooms/1/restrictions", json={"role_id": 3}, headers=organizer_headers)
    assert res3.status_code == 403


def test_create_room_duplicate_name(client, admin_headers):
    """Tạo phòng với tên đã tồn tại -> Phải trả về 400 Bad Request"""
    payload = {
        "room_name": "Phòng Trùng Tên Test",
        "capacity": 30,
        "location": "Tòa C1"
    }
    res1 = client.post("/api/v1/rooms", json=payload, headers=admin_headers)
    assert res1.status_code in [201, 400]

    # Cố tạo lần 2 với cùng tên
    res2 = client.post("/api/v1/rooms", json=payload, headers=admin_headers)
    assert res2.status_code == 400


def test_get_nonexistent_room_detail(client, organizer_headers):
    """Xem chi tiết phòng có ID không tồn tại -> Phải trả về 404"""
    res = client.get("/api/v1/rooms/99999", headers=organizer_headers)
    assert res.status_code == 404


def test_bug_availability_on_nonexistent_room(client, organizer_headers):
    """
    KIỂM THỬ LỖ HỔNG/THIẾU SÓT: Lấy timeline phòng họp không tồn tại (GET /rooms/99999/availability)
    Kỳ vọng: Trả về 404 Not Found vì phòng không tồn tại.
    Thực tế: Trả về 200 OK với danh sách rỗng [] do thiếu kiểm tra phòng tồn tại.
    """
    res = client.get("/api/v1/rooms/99999/availability?target_date=2026-10-20", headers=organizer_headers)
    if res.status_code == 200:
        pytest.fail("API BUG DETECTED: GET /rooms/{non_existent_id}/availability returns 200 OK with empty list instead of 404 Not Found!")


def test_bug_delete_room_with_active_meetings(client, admin_headers, organizer_headers):
    """
    KIỂM THỬ TÍNH TOÀN VẸN DỮ LIỆU: Xóa một phòng họp đang có lịch họp đã được lên lịch.
    Kỳ vọng: Hệ thống phải có cơ chế cảnh báo/chặn xóa hoặc hủy/dọn sạch các lịch họp tương ứng.
    Thực tế: Gọi db.delete(room) có thể gây vi phạm khóa ngoại (IntegrityError 500) hoặc để lại orphaned meetings.
    """
    # 1. Tạo phòng tạm thời (dọn sạch trước nếu đã có từ lần chạy trước)
    db = SessionLocal()
    old_room = db.query(Room).filter(Room.room_name == "Phòng Test Xóa Khi Có Lịch").first()
    if old_room:
        db.delete(old_room)
        db.commit()
    db.close()

    room_res = client.post("/api/v1/rooms", json={
        "room_name": "Phòng Test Xóa Khi Có Lịch",
        "capacity": 20,
        "location": "Tòa C5"
    }, headers=admin_headers)
    assert room_res.status_code == 201
    room_id = room_res.json()["room_id"]

    # 2. Đặt lịch tại phòng này
    tomorrow = datetime.now() + timedelta(days=2)
    meeting_res = client.post("/api/v1/meetings", json={
        "room_id": room_id,
        "title": "Cuộc họp trên phòng sắp bị xóa",
        "start_time": tomorrow.replace(hour=9, minute=0, second=0).isoformat(),
        "end_time": tomorrow.replace(hour=11, minute=0, second=0).isoformat()
    }, headers=organizer_headers)
    assert meeting_res.status_code == 201

    # 3. Admin thực hiện xóa phòng
    del_res = client.delete(f"/api/v1/rooms/{room_id}", headers=admin_headers)

    # Nếu xóa thành công mà vẫn còn meeting trỏ tới room_id đã mất, hoặc nếu server crash 500
    if del_res.status_code == 500:
        pytest.fail("DATABASE INTEGRITY ERROR (500): Server crashed with IntegrityError when deleting room that has associated meetings!")
    elif del_res.status_code == 200:
        # Kiểm tra xem meeting có còn tồn tại và trỏ tới phòng mồ côi không
        db = SessionLocal()
        m = db.query(Meeting).filter(Meeting.room_id == room_id).first()
        db.close()
        if m:
            pytest.fail("DATA INTEGRITY BUG: Room deleted successfully but left behind orphaned meeting referencing deleted room_id without cascading cancellation!")
