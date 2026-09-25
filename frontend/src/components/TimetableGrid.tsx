import React, { useState, useEffect } from 'react';
import { X, Calendar as CalendarIcon, Clock, Users } from 'lucide-react';

const TIME_SLOTS = [
  "07:00", "08:00", "09:00", "10:00", "11:00", 
  "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"
];

const API_BASE = "http://localhost:8000/api/v1";

export default function TimetableGrid() {
  const [rooms, setRooms] = useState<any[]>([]);
  const [bookings, setBookings] = useState<any[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedSlot, setSelectedSlot] = useState<{roomId: number, time: string} | null>(null);
  const [token, setToken] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  // 1. Authenticate (Mock login as Organizer)
  useEffect(() => {
    fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "organizer@ictu.vn", password: "123456" })
    })
    .then(res => res.json())
    .then(data => setToken(data.access_token))
    .catch(err => console.error("Login failed", err));
  }, []);

  // 2. Fetch Rooms & Bookings
  const fetchData = async () => {
    if (!token) return;
    try {
      const roomRes = await fetch(`${API_BASE}/rooms`, { headers: { Authorization: `Bearer ${token}` } });
      const roomData = await roomRes.json();
      setRooms(roomData);

      const bookingRes = await fetch(`${API_BASE}/meetings?from_date=${selectedDate}&to_date=${selectedDate}`, { 
        headers: { Authorization: `Bearer ${token}` } 
      });
      const bookingData = await bookingRes.json();
      setBookings(bookingData);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token, selectedDate]);

  const handleCellClick = (roomId: number, time: string, isRestricted: boolean, hasBooking: boolean) => {
    if (isRestricted || hasBooking) return;
    setSelectedSlot({ roomId, time });
    setError("");
  };

  const handleBooking = async () => {
    if (!title.trim()) {
      setError("Vui lòng nhập tên cuộc họp");
      return;
    }
    
    // Parse time to ISO
    const start_time = `${selectedDate}T${selectedSlot?.time}:00`;
    // Add 1 hour to end time for simplicity
    const [h, m] = selectedSlot!.time.split(':');
    const endHour = parseInt(h) + 1;
    const end_time = `${selectedDate}T${endHour.toString().padStart(2, '0')}:${m}:00`;

    try {
      const res = await fetch(`${API_BASE}/meetings`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({
          room_id: selectedSlot?.roomId,
          title: title,
          description: description,
          start_time,
          end_time
        })
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || "Có lỗi xảy ra");
        return;
      }

      // Success
      setSelectedSlot(null);
      setTitle("");
      setDescription("");
      fetchData(); // reload
    } catch (err: any) {
      setError("Lỗi kết nối API");
    }
  };

  return (
    <div className="ledger-container">
      <div className="ledger-header">
        <h1>Lịch phòng họp ICTU</h1>
        <div className="ledger-filters">
          <input 
            type="date" 
            className="form-input" 
            value={selectedDate} 
            onChange={(e) => setSelectedDate(e.target.value)} 
          />
        </div>
      </div>

      <div className="ledger-grid-wrapper">
        <div 
          className="ledger-grid" 
          style={{ gridTemplateColumns: `80px repeat(${rooms.length || 1}, minmax(180px, 1fr))` }}
        >
          {/* Header Row */}
          <div className="ledger-col-header-corner"></div>
          {rooms.map(room => (
            <div key={room.room_id} className="ledger-col-header">
              {room.room_name}
              <div style={{ fontSize: '0.75rem', color: 'var(--color-gray-600)', fontWeight: 400 }}>
                {room.capacity} chỗ
              </div>
            </div>
          ))}

          {/* Grid Rows */}
          {TIME_SLOTS.map(time => (
            <React.Fragment key={time}>
              <div className="ledger-time-label">{time}</div>
              {rooms.map(room => {
                // Find booking in this slot
                const booking = bookings.find(b => {
                  if (b.room_id !== room.room_id || b.status === "CANCELLED") return false;
                  const bTime = b.start_time.split('T')[1].substring(0, 5);
                  return bTime === time;
                });
                
                // Real role restriction mapping (simplified logic: >0 restrictions -> restricted)
                const isRestricted = room.restrictions?.length > 0; 
                
                return (
                  <div 
                    key={`${room.room_id}-${time}`} 
                    className={`ledger-cell ${booking ? 'is-booked' : ''} ${isRestricted && !booking ? 'is-restricted' : ''}`}
                    onClick={() => handleCellClick(room.room_id, time, isRestricted, !!booking)}
                  >
                    {booking && (
                      <div className="booking-block">
                        <div className="booking-title">{booking.title}</div>
                        <div className="booking-org">ID: {booking.organizer_id}</div>
                      </div>
                    )}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Booking Modal */}
      {selectedSlot && (
        <div className="modal-overlay" onClick={() => setSelectedSlot(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Đặt phòng</h2>
              <button className="modal-close" onClick={() => setSelectedSlot(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', color: 'var(--color-gray-600)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CalendarIcon size={16} />
                  <span>{rooms.find(r => r.room_id === selectedSlot.roomId)?.room_name}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Clock size={16} />
                  <span>{selectedSlot.time} ({selectedDate})</span>
                </div>
              </div>

              {error && <div style={{ color: 'red', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}

              <div className="form-group">
                <label className="form-label">Tên cuộc họp</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="Nhập tiêu đề cuộc họp..." 
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  autoFocus 
                />
              </div>
              <div className="form-group">
                <label className="form-label">Ghi chú</label>
                <textarea 
                  className="form-input" 
                  rows={3} 
                  placeholder="Yêu cầu thiết bị, v.v."
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                ></textarea>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setSelectedSlot(null)}>Hủy</button>
              <button className="btn btn-primary" onClick={handleBooking}>Xác nhận đặt</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
