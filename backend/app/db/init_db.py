from sqlalchemy.orm import Session
from app.core.database import Base, engine
from app.models import Role, Department, User, Room, RoomRestriction
from app.core.security import get_password_hash

def init_db(db: Session) -> None:
    # 1. Tạo tất cả bảng nếu chưa có (bao gồm rooms, room_restrictions)
    Base.metadata.create_all(bind=engine)

    # 2. Khởi tạo các vai trò (Roles) mặc định nếu chưa tồn tại
    default_roles = ["ADMIN", "ORGANIZER", "PARTICIPANT"]
    roles_map = {}
    for r_name in default_roles:
        role = db.query(Role).filter(Role.role_name == r_name).first()
        if not role:
            role = Role(role_name=r_name)
            db.add(role)
            db.commit()
            db.refresh(role)
        roles_map[r_name] = role.role_id

    # 3. Khởi tạo một số phòng ban (Departments) mẫu
    departments_data = [
        {"name": "Khoa Công nghệ thông tin", "hrm": "DEPT_CNTT"},
        {"name": "Phòng Đào tạo & Quản lý sinh viên", "hrm": "DEPT_DT"},
        {"name": "Phòng Hành chính & Tổng hợp", "hrm": "DEPT_HC"},
    ]
    dept_map = {}
    for d_data in departments_data:
        dept = db.query(Department).filter(Department.department_name == d_data["name"]).first()
        if not dept:
            dept = Department(department_name=d_data["name"], hrm_code=d_data["hrm"])
            db.add(dept)
            db.commit()
            db.refresh(dept)
        dept_map[d_data["name"]] = dept.department_id

    # 4. Tạo tài khoản Admin mặc định nếu chưa có
    admin_email = "admin@ictu.vn"
    admin_user = db.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        admin_user = User(
            email=admin_email,
            password_hash=get_password_hash("Admin@123"),
            full_name="Quản trị viên Hệ thống",
            phone="0987654321",
            role_id=roles_map["ADMIN"],
            department_id=dept_map.get("Phòng Hành chính & Tổng hợp"),
            status="ACTIVE"
        )
        db.add(admin_user)
        db.commit()
        print(">> Đã khởi tạo tài khoản Admin mặc định: admin@ictu.vn / Admin@123")

    # 5. Tạo tài khoản Giảng viên / Người đặt lịch mẫu
    organizer_email = "organizer@ictu.vn"
    organizer_user = db.query(User).filter(User.email == organizer_email).first()
    if not organizer_user:
        organizer_user = User(
            email=organizer_email,
            password_hash=get_password_hash("123456"),
            full_name="Nguyễn Văn A (Giảng viên)",
            phone="0912345678",
            role_id=roles_map["ORGANIZER"],
            department_id=dept_map.get("Khoa Công nghệ thông tin"),
            status="ACTIVE"
        )
        db.add(organizer_user)
        db.commit()
        print(">> Đã khởi tạo tài khoản Organizer mẫu: organizer@ictu.vn / 123456")

    # 6. Khởi tạo một số phòng họp mẫu (Rooms - US #7, #10)
    sample_rooms = [
        {
            "name": "Hội trường lớn C1",
            "capacity": 150,
            "location": "Tầng 1, Tòa nhà C1",
            "description": "Màn hình LED lớn, hệ thống âm thanh hội thảo, điều hòa trung tâm",
            "status": "AVAILABLE"
        },
        {
            "name": "Phòng họp Ban Giám hiệu (A1-201)",
            "capacity": 30,
            "location": "Tầng 2, Tòa nhà Điều hành A1",
            "description": "Bàn tròn VIP, micro từng vị trí, màn hình TV 85 inch",
            "status": "AVAILABLE"
        },
        {
            "name": "Phòng hội thảo Khoa CNTT (C1-402)",
            "capacity": 60,
            "location": "Tầng 4, Tòa nhà C1",
            "description": "Máy chiếu 4K, 2 micro không dây, wifi tốc độ cao",
            "status": "AVAILABLE"
        },
        {
            "name": "Phòng họp chuyên đề (C1-305)",
            "capacity": 25,
            "location": "Tầng 3, Tòa nhà C1",
            "description": "Bảng thông minh Smartboard, bàn ghế di động linh hoạt",
            "status": "AVAILABLE"
        },
        {
            "name": "Phòng họp nhóm sinh viên (B-102)",
            "capacity": 15,
            "location": "Tầng 1, Tòa nhà B",
            "description": "TV 65 inch, cổng kết nối HDMI/Type-C",
            "status": "AVAILABLE"
        },
        {
            "name": "Phòng đa năng C2 (Đang bảo trì)",
            "capacity": 50,
            "location": "Tầng 2, Tòa nhà C2",
            "description": "Đang bảo trì hệ thống điều hòa và ánh sáng",
            "status": "MAINTENANCE"
        }
    ]

    for r_data in sample_rooms:
        room = db.query(Room).filter(Room.room_name == r_data["name"]).first()
        if not room:
            room = Room(
                room_name=r_data["name"],
                capacity=r_data["capacity"],
                location=r_data["location"],
                description=r_data["description"],
                status=r_data["status"]
            )
            db.add(room)
            db.commit()
            db.refresh(room)

            # Cấu hình giới hạn mẫu (US #21):
            # Phòng Ban Giám hiệu (A1-201) chỉ dành cho Admin và Giảng viên, cấm PARTICIPANT (sinh viên) đặt
            if "Ban Giám hiệu" in room.room_name and "PARTICIPANT" in roles_map:
                restriction = RoomRestriction(
                    room_id=room.room_id,
                    role_id=roles_map["PARTICIPANT"],
                    notes="Chỉ cán bộ giảng viên và ban giám hiệu mới được đặt phòng này"
                )
                db.add(restriction)
                db.commit()
    print(">> Đã khởi tạo danh sách phòng họp mẫu thành công!")
