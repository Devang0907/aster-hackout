import { getToken } from "./auth";

const API_BASE_URL = (import.meta.env as any)["VITE_API_BASE_URL"] || "http://localhost:8000";

export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Token expired or invalid, clear auth
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
    window.location.href = "/signin";
    throw new Error("Unauthorized");
  }

  return response;
}

export async function get(endpoint: string): Promise<Response> {
  return apiRequest(endpoint, { method: "GET" });
}

export async function post(endpoint: string, data: any): Promise<Response> {
  return apiRequest(endpoint, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function patch(endpoint: string, data: any): Promise<Response> {
  return apiRequest(endpoint, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function del(endpoint: string): Promise<Response> {
  return apiRequest(endpoint, { method: "DELETE" });
}
