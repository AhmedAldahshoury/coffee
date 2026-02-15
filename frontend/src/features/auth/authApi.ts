import { httpClient } from '../../shared/api/httpClient';

export interface AuthPayload { email: string; password: string }
export interface AuthResponse { access_token: string; token_type: string }

export async function login(payload: AuthPayload) {
  const { data } = await httpClient.post<AuthResponse>('/auth/login', payload);
  return data;
}

export async function register(payload: AuthPayload) {
  const { data } = await httpClient.post<AuthResponse>('/auth/register', payload);
  return data;
}
