import axios, { AxiosError } from 'axios';

export const apiBaseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

export const httpClient = axios.create({
  baseURL: apiBaseUrl,
  headers: { 'Content-Type': 'application/json' },
});

httpClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('coffee_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function formatApiError(error: unknown): string {
  const fallback = 'Unexpected error';
  if (!error) return fallback;

  const axiosError = error as AxiosError<{ detail?: string }>;
  const status = axiosError.response?.status;
  const detail = axiosError.response?.data?.detail;

  if (status) {
    return `HTTP ${status}: ${detail ?? axiosError.message}`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
}
