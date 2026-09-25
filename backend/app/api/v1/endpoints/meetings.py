from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.core.database import get_db
from app.models.meeting import Meeting, MeetingParticipant
from app.models.room import Room, RoomRestriction
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingOut, MeetingRespond, RoomAvailability
from app.api.deps import get_current_active_user, require_roles

router = APIRouter()

@router.post("", response_model=MeetingOut, status_code=status.HTTP_201_CREATED, summary="Tạo lịch họp mới (US #1, #4)")
def create_meeting(
    data: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if data.start_time >= data.end_time:
        raise HTTPException(status_code=400, detail="Thời gian kết thúc phải sau thời gian bắt đầu")
    
    # 1. Kiểm tra phòng tồn tại và quyền truy cập
    room = db.query(Room).filter(Room.room_id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Không tìm thấy phòng họp")
    if room.status != "AVAILABLE":
        raise HTTPException(status_code=400, detail="Phòng đang bảo trì, không thể đặt")
    
    # Kiem tra quyen dat phong
    if current_user.role.role_name != "ADMIN":
        restrictions = db.query(RoomRestriction).filter(RoomRestriction.room_id == data.room_id).all()
        if restrictions:
            allowed_roles = [r.role_id for r in restrictions]
            if current_user.role_id not in allowed_roles:
                raise HTTPException(status_code=403, detail="Bạn không có quyền đặt phòng này")

    # 2. Thuật toán chống trùng lịch (Conflict Detection)
    conflict = db.query(Meeting).filter(
        Meeting.room_id == data.room_id,
        Meeting.status != "CANCELLED",
        Meeting.start_time < data.end_time,
        Meeting.end_time > data.start_time
    ).first()
    
    if conflict:
        raise HTTPException(
            status_code=409,
            detail=f"Trùng lịch! Phòng đã được đặt từ {conflict.start_time} đến {conflict.end_time}"
        )

    # 3. Tạo cuộc họp
    meeting = Meeting(
        organizer_id=current_user.user_id,
        room_id=data.room_id,
        title=data.title,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        status="SCHEDULED"
    )
    db.add(meeting)
    db.flush() # get meeting_id
    
    # 4. Thêm người tham gia
    if data.participant_ids:
        for uid in set(data.participant_ids):
            # check if user exists
            u = db.query(User).filter(User.user_id == uid).first()
            if u:
                participant = MeetingParticipant(meeting_id=meeting.meeting_id, user_id=uid, status="PENDING")
                db.add(participant)
            
    db.commit()
    db.refresh(meeting)
    return meeting

@router.get("", response_model=List[MeetingOut], summary="Xem danh sách lịch họp")
def list_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    room_id: Optional[int] = None,
    user_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Meeting)
    
    if room_id:
        query = query.filter(Meeting.room_id == room_id)
    if user_id:
        # Lay lich do user to chuc hoac duoc moi
        query = query.join(MeetingParticipant, isouter=True).filter(
            or_(Meeting.organizer_id == user_id, MeetingParticipant.user_id == user_id)
        )
    if from_date:
        query = query.filter(Meeting.start_time >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.filter(Meeting.end_time <= datetime.combine(to_date, datetime.max.time()))
        
    meetings = query.offset(skip).limit(limit).all()
    return meetings

@router.put("/{meeting_id}", response_model=MeetingOut, summary="Sửa thông tin lịch họp (US #2)")
def update_meeting(
    meeting_id: int,
    data: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    meeting = db.query(Meeting).filter(Meeting.meeting_id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch họp")
        
    if meeting.organizer_id != current_user.user_id and current_user.role.role_name != "ADMIN":
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa cuộc họp này")
        
    if data.start_time and data.end_time:
        if data.start_time >= data.end_time:
            raise HTTPException(status_code=400, detail="Thời gian kết thúc phải sau thời gian bắt đầu")
            
        # Kiem tra conflict moi
        conflict = db.query(Meeting).filter(
            Meeting.room_id == (data.room_id or meeting.room_id),
            Meeting.meeting_id != meeting_id,
            Meeting.status != "CANCELLED",
            Meeting.start_time < data.end_time,
            Meeting.end_time > data.start_time
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail="Trùng lịch với cuộc họp khác")
            
    if data.room_id is not None: meeting.room_id = data.room_id
    if data.title is not None: meeting.title = data.title
    if data.description is not None: meeting.description = data.description
    if data.start_time is not None: meeting.start_time = data.start_time
    if data.end_time is not None: meeting.end_time = data.end_time
    if data.status is not None: meeting.status = data.status
    
    db.commit()
    db.refresh(meeting)
    return meeting

@router.patch("/{meeting_id}/cancel", summary="Hủy lịch họp (US #2, #9)")
def cancel_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    meeting = db.query(Meeting).filter(Meeting.meeting_id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch họp")
    if meeting.organizer_id != current_user.user_id and current_user.role.role_name != "ADMIN":
        raise HTTPException(status_code=403, detail="Bạn không có quyền hủy cuộc họp này")
        
    meeting.status = "CANCELLED"
    db.commit()
    return {"message": "Đã hủy cuộc họp"}

@router.patch("/{meeting_id}/respond", summary="Phản hồi lời mời (Chấp nhận / Từ chối)")
def respond_meeting(
    meeting_id: int,
    data: MeetingRespond,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if data.status not in ["ACCEPTED", "DECLINED"]:
        raise HTTPException(status_code=400, detail="Trạng thái phản hồi không hợp lệ")
        
    participant = db.query(MeetingParticipant).filter(
        MeetingParticipant.meeting_id == meeting_id,
        MeetingParticipant.user_id == current_user.user_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Bạn không được mời tham gia cuộc họp này")
        
    participant.status = data.status
    db.commit()
    return {"message": f"Bạn đã {data.status} lời mời"}
