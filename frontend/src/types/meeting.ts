export interface Room {
  room_id: number;
  room_name: string;
  capacity: number;
  location?: string;
  status: string;
  description?: string;
  restrictions?: Array<{
    restriction_id: number;
    role_id: number;
    notes?: string;
  }>;
}

export interface Meeting {
  meeting_id: number;
  organizer_id: number;
  room_id: number;
  title: string;
  description?: string | null;
  start_time: string;
  end_time: string;
  status: string;
  created_at: string;
  participants?: Array<{
    participant_id: number;
    user_id: number;
    status: string;
  }>;
}

export interface CreateMeetingPayload {
  room_id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  participant_ids?: number[];
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  full_name: string;
  email: string;
  role: string;
}
