export type User = {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
};

export type Organization = {
  id: string;
  name: string;
  slug: string;
};

export type Project = {
  id: string;
  organization_id: string;
  name: string;
  slug: string;
};

export type PowerCurve = {
  id: string;
  name: string;
  turbine_model: string;
  points: { wind_speed_m_s: number; power_kw: number }[];
};

export type EnergyAssessment = {
  id: string;
  name: string;
  power_curve: string;
  wake_loss_fraction: number;
  method_version: string;
  results: {
    plant_net_aep_mwh?: number;
    plant_gross_aep_mwh?: number;
    turbine_count?: number;
    method_version?: string;
  };
  created_at: string;
};

export type TurbinePosition = {
  id: string;
  label: string;
  x: number;
  y: number;
};

const TOKEN_KEY = "wind_platform_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }
  const token = getToken();
  if (token) headers.set("Authorization", `Token ${token}`);

  const response = await fetch(path, { ...init, headers });
  if (response.status === 204) return undefined as T;

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const detail =
      (data && (data.detail || data.non_field_errors?.[0])) ||
      `Request failed (${response.status})`;
    throw new ApiError(response.status, String(detail));
  }
  return data as T;
}

export const api = {
  login: (username: string, password: string) =>
    request<{ token: string }>("/api/v1/auth/login/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  logout: () => request<{ detail: string }>("/api/v1/auth/logout/", { method: "POST" }),
  me: () => request<User>("/api/v1/auth/me/"),
  organizations: () => request<Organization[]>("/api/v1/organizations/"),
  createOrganization: (name: string) =>
    request<Organization>("/api/v1/organizations/", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  projects: (orgId: string) =>
    request<Project[]>(`/api/v1/organizations/${orgId}/projects/`),
  createProject: (orgId: string, name: string) =>
    request<Project>(`/api/v1/organizations/${orgId}/projects/`, {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  project: (projectId: string) => request<Project>(`/api/v1/projects/${projectId}/`),
  turbines: (projectId: string) =>
    request<TurbinePosition[]>(`/api/v1/projects/${projectId}/turbines/`),
  powerCurves: () => request<PowerCurve[]>("/api/v1/energy/power-curves/"),
  assessments: (projectId: string) =>
    request<EnergyAssessment[]>(`/api/v1/projects/${projectId}/energy-assessments/`),
  createAssessment: (
    projectId: string,
    payload: {
      name: string;
      power_curve: string;
      wind_distribution: { ws_m_s: number; hours: number }[];
      wake_loss_fraction: number;
    },
  ) =>
    request<EnergyAssessment>(`/api/v1/projects/${projectId}/energy-assessments/`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
