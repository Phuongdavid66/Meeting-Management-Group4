import React, { useEffect, useState } from "react";
import { Calendar as CalendarIcon, Clock } from "lucide-react";
import { ApiError } from "../api/httpClient";
import Toast from "./Toast";
import Button from "./Button";
import Modal from "./Modal";
import { Input, Textarea } from "./Input";
import { login } from "../services/authService";
import {
  createMeeting,
  getMeetings,
  getRooms,
} from "../services/meetingService";
import type { Meeting, Room } from "../types/meeting";

const TIME_SLOTS = [
  "07:00",
  "08:00",
  "09:00",
  "10:00",
  "11:00",
  "12:00",
  "13:00",
  "14:00",
  "15:00",
  "16:00",
  "17:00",
];

interface SelectedSlot {
  roomId: number;
  time: string;
}

function getLocalDateString() {
  const date = new Date();
  const offset = date.getTimezoneOffset();
  const localDate = new Date(date.getTime() - offset * 60_000);
  return localDate.toISOString().split("T")[0];
}

export default function TimetableGrid() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [bookings, setBookings] = useState<Meeting[]>([]);
  const [selectedDate, setSelectedDate] = useState(getLocalDateString());
  const [selectedSlot, setSelectedSlot] = useState<SelectedSlot | null>(null);

  const [token, setToken] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(false);
  const [toast, setToast] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  // Demo authentication: backend currently provides a seeded organizer account.
  useEffect(() => {
    let cancelled = false;

    login("organizer@ictu.vn", "123456")
      .then((data) => {
        if (!cancelled) {
          setToken(data.access_token);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const message =
            err instanceof ApiError ? err.detail : "Không thể đăng nhập Backend.";
          setError(message);
          setToast({ type: "error", message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const fetchData = async () => {
    if (!token) return;

    setLoadingData(true);
    try {
      const [roomData, meetingData] = await Promise.all([
        getRooms(token),
        getMeetings(token, selectedDate),
      ]);

      setRooms(roomData);
      setBookings(meetingData);
    } catch (err: unknown) {
      const message =
        err instanceof ApiError
          ? err.detail
          : "Không thể tải dữ liệu lịch họp.";
      setError(message);
    } finally {
      setLoadingData(false);
    }
  };

  useEffect(() => {
    void fetchData();
  }, [token, selectedDate]);

  const handleCellClick = (
    roomId: number,
    time: string,
    isRestricted: boolean,
    hasBooking: boolean,
  ) => {
    if (isRestricted || hasBooking || loading) return;

    setSelectedSlot({ roomId, time });
    setError("");
  };

  const handleBooking = async () => {
    if (!selectedSlot || !token) return;

    if (!title.trim()) {
      setError("Vui lòng nhập tên cuộc họp");
      return;
    }

    const startTime = `${selectedDate}T${selectedSlot.time}:00`;
    const [hour, minute] = selectedSlot.time.split(":");
    const endHour = Number(hour) + 1;
    const endTime = `${selectedDate}T${String(endHour).padStart(2, "0")}:${minute}:00`;

    setLoading(true);
    setError("");

    try {
      await createMeeting(token, {
        room_id: selectedSlot.roomId,
        title: title.trim(),
        description: description.trim() || undefined,
        start_time: startTime,
        end_time: endTime,
      });

      // Reset form only after Backend confirms HTTP 201.
      setSelectedSlot(null);
      setTitle("");
      setDescription("");
      setError("");

      setToast({
        type: "success",
        message: "Tạo lịch họp thành công!",
      });

      await fetchData();
    } catch (err: unknown) {
      const message =
        err instanceof ApiError
          ? err.detail
          : "Lỗi kết nối API. Vui lòng kiểm tra Backend.";

      setError(message);
      setToast({ type: "error", message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ledger-container">
      <div className="ledger-header">
        <div>
          <h1>Lịch phòng họp ICTU</h1>
          {loadingData && (
            <span className="data-loading-text">Đang cập nhật lịch...</span>
          )}
        </div>

        <div className="ledger-filters">
          <input
            type="date"
            className="form-input"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            disabled={loading}
          />
        </div>
      </div>

      <div className="ledger-grid-wrapper">
        <div
          className="ledger-grid"
          style={{
            "--room-count": rooms.length || 1,
          } as React.CSSProperties}
        >
          <div className="ledger-col-header-corner" />

          {rooms.map((room) => (
            <div key={room.room_id} className="ledger-col-header">
              {room.room_name}
              <div
                style={{
                  fontSize: "0.75rem",
                  color: "var(--color-gray-600)",
                  fontWeight: 400,
                }}
              >
                {room.capacity} chỗ
              </div>
            </div>
          ))}

          {TIME_SLOTS.map((time) => (
            <React.Fragment key={time}>
              <div className="ledger-time-label">{time}</div>

              {rooms.map((room) => {
                const booking = bookings.find((item) => {
                  if (
                    item.room_id !== room.room_id ||
                    item.status === "CANCELLED"
                  ) {
                    return false;
                  }

                  const bookingTime = item.start_time
                    .split("T")[1]
                    ?.substring(0, 5);

                  return bookingTime === time;
                });

                const isRestricted = (room.restrictions?.length ?? 0) > 0;

                return (
                  <div
                    key={`${room.room_id}-${time}`}
                    className={`ledger-cell ${booking ? "is-booked" : ""} ${
                      isRestricted && !booking ? "is-restricted" : ""
                    }`}
                    onClick={() =>
                      handleCellClick(
                        room.room_id,
                        time,
                        isRestricted,
                        Boolean(booking),
                      )
                    }
                  >
                    {booking && (
                      <div className="booking-block">
                        <div className="booking-title">{booking.title}</div>
                        <div className="booking-org">
                          ID: {booking.organizer_id}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>

      <Modal
        open={Boolean(selectedSlot)}
        title="Đặt phòng"
        onClose={() => !loading && setSelectedSlot(null)}
        closeDisabled={loading}
        footer={
          <>
            <Button
              variant="ghost"
              type="button"
              onClick={() => setSelectedSlot(null)}
              disabled={loading}
            >
              Hủy
            </Button>
            <Button
              variant="primary"
              type="button"
              onClick={() => void handleBooking()}
              disabled={loading}
            >
              {loading ? "Đang tạo..." : "Xác nhận đặt"}
            </Button>
          </>
        }
      >
        {selectedSlot && (
          <>
            <div className="booking-meta">
              <div className="booking-meta-item">
                <CalendarIcon size={16} aria-hidden="true" />
                <span>
                  {rooms.find((room) => room.room_id === selectedSlot.roomId)?.room_name}
                </span>
              </div>
              <div className="booking-meta-item">
                <Clock size={16} aria-hidden="true" />
                <span>{selectedSlot.time} ({selectedDate})</span>
              </div>
            </div>

            {error && (
              <div className="form-error" role="alert">
                {error}
              </div>
            )}

            <Input
              id="meeting-title"
              label="Tên cuộc họp"
              type="text"
              placeholder="Nhập tiêu đề cuộc họp..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={loading}
              autoFocus
            />

            <Textarea
              id="meeting-description"
              label="Ghi chú"
              rows={3}
              placeholder="Yêu cầu thiết bị, v.v."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={loading}
            />
          </>
        )}
      </Modal>

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
