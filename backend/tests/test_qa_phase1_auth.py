"""
QA Test Suite - Phase 1: Authentication, Authorization & User Management
Tập trung kiểm thử các kịch bản biên, bảo mật, và lỗ hổng tiềm ẩn.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.db.init_db import init_db
from app.models.user import User

@pytest.fixture(scope="module")
def client():
    db = SessionLocal()
    init_db(db)
    db.close()
    return TestClient(app)

@pytest.fixture(scope="module")
def admin_token(client):
    res = client.post("/api/v1/auth/login", json={"email": "admin@ictu.vn", "password": "Admin@123"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def organizer_token(client):
    res = client.post("/api/v1/auth/login", json={"email": "organizer@ictu.vn", "password": "123456"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def participant_token(client, admin_token):
    # Ensure student exists
    res = client.get("/api/v1/users?search=student1@ictu.vn", headers={"Authorization": f"Bearer {admin_token}"})
    if not res.json():
        client.post("/api/v1/users", json={
            "email": "student1@ictu.vn",
            "password": "password123",
            "full_name": "Nguyen Van Sinh Vien",
            "role_id": 3,
            "status": "ACTIVE"
        }, headers={"Authorization": f"Bearer {admin_token}"})
    res_login = client.post("/api/v1/auth/login", json={"email": "student1@ictu.vn", "password": "password123"})
    return res_login.json()["access_token"]


def test_login_invalid_password(client):
    """Test đăng nhập sai mật khẩu -> Phải trả về 400"""
    res = client.post("/api/v1/auth/login", json={"email": "admin@ictu.vn", "password": "WrongPassword"})
    assert res.status_code == 400
    assert "detail" in res.json()


def test_login_nonexistent_email(client):
    """Test đăng nhập email không tồn tại -> Phải trả về 400"""
    res = client.post("/api/v1/auth/login", json={"email": "nonexistent_user@ictu.vn", "password": "AnyPassword"})
    assert res.status_code == 400


def test_login_inactive_user(client, admin_token):
    """Test người dùng có status=INACTIVE thì không được phép đăng nhập"""
    # Tạo user INACTIVE (dọn sạch nếu có từ lần chạy trước)
    db = SessionLocal()
    old_inact = db.query(User).filter(User.email == "inactive_test@ictu.vn").first()
    if old_inact:
        db.delete(old_inact)
        db.commit()
    db.close()

    temp_email = "inactive_test@ictu.vn"
    client.post("/api/v1/users", json={
        "email": temp_email,
        "password": "password123",
        "full_name": "Inactive User",
        "role_id": 3,
        "status": "INACTIVE"
    }, headers={"Authorization": f"Bearer {admin_token}"})

    res = client.post("/api/v1/auth/login", json={"email": temp_email, "password": "password123"})
    assert res.status_code == 403, f"Expected 403 for inactive user login, got {res.status_code}"


def test_access_without_token(client):
    """Gọi endpoint bảo mật mà không có Authorization header -> Phải trả về 401"""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_access_with_malformed_token(client):
    """Gọi endpoint bảo mật với Token rác -> Phải trả về 401"""
    res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_garbage_token_123"})
    assert res.status_code == 401


def test_change_password_validation(client, participant_token):
    """Đổi mật khẩu với mật khẩu mới < 6 ký tự hoặc sai mật khẩu cũ -> Phải trả về 400"""
    # 1. Sai mật khẩu cũ
    res1 = client.post("/api/v1/auth/change-password", json={
        "old_password": "IncorrectOldPassword",
        "new_password": "validNewPassword123"
    }, headers={"Authorization": f"Bearer {participant_token}"})
    assert res1.status_code == 400

    # 2. Mật khẩu mới quá ngắn (< 6 ký tự)
    res2 = client.post("/api/v1/auth/change-password", json={
        "old_password": "password123",
        "new_password": "123"
    }, headers={"Authorization": f"Bearer {participant_token}"})
    assert res2.status_code == 400


def test_security_flaw_password_bypass_via_update_user(client, admin_token):
    """
    KIỂM THỬ LỖ HỔNG: PUT /api/v1/users/{id} cho phép đổi mật khẩu mà không cần mật khẩu cũ,
    và không kiểm tra độ dài tối thiểu (< 6 ký tự).
    """
    # Tạo 1 user để thử nghiệm (dọn sạch nếu có từ lần chạy trước)
    db = SessionLocal()
    old_u = db.query(User).filter(User.email == "bypass_victim@ictu.vn").first()
    if old_u:
        db.delete(old_u)
        db.commit()
    db.close()

    email = "bypass_victim@ictu.vn"
    create_res = client.post("/api/v1/users", json={
        "email": email,
        "password": "OriginalPassword123",
        "full_name": "Bypass Victim",
        "role_id": 3,
        "status": "ACTIVE"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_res.status_code == 201
    user_id = create_res.json()["user_id"]

    # Đăng nhập lấy token của user này
    user_token = client.post("/api/v1/auth/login", json={"email": email, "password": "OriginalPassword123"}).json()["access_token"]

    # User tự gọi PUT /api/v1/users/{user_id} với mật khẩu mới siêu ngắn "1" mà không cần mật khẩu cũ
    update_res = client.put(f"/api/v1/users/{user_id}", json={
        "password": "1"
    }, headers={"Authorization": f"Bearer {user_token}"})

    # Nếu hệ thống cho phép đổi thành công mà không đòi old_password hoặc không validate len >= 6:
    # Đây là một điểm yếu bảo mật cần ghi nhận vào Bug Report!
    if update_res.status_code == 200:
        # Kiểm tra xem có thể đăng nhập bằng mật khẩu '1' không
        test_login = client.post("/api/v1/auth/login", json={"email": email, "password": "1"})
        assert test_login.status_code == 200, "User logged in with unvalidated 1-char password!"
        # Đánh dấu bug bảo mật phát hiện được
        pytest.fail("SECURITY BUG DETECTED: User can bypass /change-password requirements via PUT /users/{id} without old password verification and without minimum length check!")


def test_admin_self_deactivation_risk(client, admin_token):
    """
    KIỂM THỬ RỦI RO: Admin tự vô hiệu hóa tài khoản của chính mình (DELETE /api/v1/users/{admin_id})
    """
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    admin_id = me_res.json()["user_id"]

    # Admin cố tự xóa/deactivate chính mình
    del_res = client.delete(f"/api/v1/users/{admin_id}", headers={"Authorization": f"Bearer {admin_token}"})

    # Nếu API cho phép xóa chính tài khoản admin đang đăng nhập mà không có bất kỳ cảnh báo/chặn nào
    if del_res.status_code == 200:
        # Khôi phục lại trạng thái ACTIVE cho admin để không hỏng test sau
        db = SessionLocal()
        admin_obj = db.query(User).filter(User.user_id == admin_id).first()
        admin_obj.status = "ACTIVE"
        db.commit()
        db.close()
        pytest.fail("LOGIC FLAW: Admin is allowed to deactivate their own active account, risking complete admin lockout!")
