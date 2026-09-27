import { apiRequest } from "../api/httpClient";
import type {
  CreateMeetingPayload,
  Meeting,
  Room,
} from "../types/meeting";

export async function getRooms(token: string): Promise<Room[]> {
  return apiRequest<Room[]>("/rooms", {}, token);
}

export async function getMeetings(
  token: string,
  date: string,
): Promise<Meeting[]> {
  const params = new URLSearchParams({
    from_date: date,
    to_date: date,
  });

  return apiRequest<Meeting[]>(`/meetings?${params.toString()}`, {}, token);
}

export async function createMeeting(
  token: string,
  payload: CreateMeetingPayload,
): Promise<Meeting> {
  return apiRequest<Meeting>(
    "/meetings",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    token,
  );
}
