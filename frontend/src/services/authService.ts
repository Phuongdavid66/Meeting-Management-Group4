import { apiRequest } from "../api/httpClient";
import type { LoginResponse } from "../types/meeting";

export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  return apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}
