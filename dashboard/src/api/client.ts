import type { ApiResponse, DashboardData } from "../types/dashboard";

export async function fetchDashboard(): Promise<DashboardData> {
  const response = await fetch("/api/v1/dashboard");
  if (!response.ok) {
    throw new Error(`Dashboard request failed (${response.status})`);
  }
  const body = (await response.json()) as ApiResponse<DashboardData>;
  if (!body.success || !body.data) {
    throw new Error(body.message || "Dashboard request failed");
  }
  return body.data;
}
