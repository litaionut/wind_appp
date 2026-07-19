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

export type TurbineModel = {
  id: string;
  manufacturer: string;
  manufacturer_name: string;
  name: string;
  hub_height_m: number;
  rotor_diameter_m: number;
  rated_power_kw: number;
};

export type TurbinePosition = {
  id: string;
  label: string;
  x: number;
  y: number;
  z: number | null;
  turbine_model: string | null;
  turbine_model_name: string | null;
};

export type PowerCurve = {
  id: string;
  name: string;
  turbine_model: string;
  points: { wind_speed_m_s: number; power_kw: number }[];
};

export type CtCurve = {
  id: string;
  name: string;
  turbine_model: string;
  points: { wind_speed_m_s: number; ct: number }[];
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

function errorDetail(data: unknown, status: number): string {
  if (data && typeof data === "object") {
    const obj = data as Record<string, unknown>;
    if (typeof obj.detail === "string") return obj.detail;
    if (Array.isArray(obj.non_field_errors) && obj.non_field_errors[0]) {
      return String(obj.non_field_errors[0]);
    }
  }
  return `Request failed (${status})`;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const isForm = typeof FormData !== "undefined" && init.body instanceof FormData;
  if (!headers.has("Content-Type") && init.body && !isForm) {
    headers.set("Content-Type", "application/json");
  }
  const token = getToken();
  if (token) headers.set("Authorization", `Token ${token}`);

  const response = await fetch(path, { ...init, headers });
  if (response.status === 204) return undefined as T;

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new ApiError(response.status, errorDetail(data, response.status));
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
  turbineModels: () => request<TurbineModel[]>("/api/v1/gis/turbine-models/"),
  createTurbineModel: (payload: {
    manufacturer_name_write: string;
    name: string;
    hub_height_m: number;
    rotor_diameter_m: number;
    rated_power_kw: number;
  }) =>
    request<TurbineModel>("/api/v1/gis/turbine-models/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  turbines: (projectId: string) =>
    request<TurbinePosition[]>(`/api/v1/projects/${projectId}/turbines/`),
  createTurbine: (
    projectId: string,
    payload: {
      label: string;
      x: number;
      y: number;
      z?: number | null;
      turbine_model: string;
    },
  ) =>
    request<TurbinePosition>(`/api/v1/projects/${projectId}/turbines/`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateTurbine: (
    projectId: string,
    turbineId: string,
    payload: Partial<{
      label: string;
      x: number;
      y: number;
      z: number | null;
      turbine_model: string | null;
    }>,
  ) =>
    request<TurbinePosition>(`/api/v1/projects/${projectId}/turbines/${turbineId}/`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  deleteTurbine: (projectId: string, turbineId: string) =>
    request<void>(`/api/v1/projects/${projectId}/turbines/${turbineId}/`, {
      method: "DELETE",
    }),
  importTurbines: (projectId: string, file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<{ created: number; updated: number }>(
      `/api/v1/projects/${projectId}/turbines/import/`,
      { method: "POST", body },
    );
  },
  importCatalogue: (file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<{ created: number; updated: number }>(
      "/api/v1/gis/turbine-catalogue/import/",
      { method: "POST", body },
    );
  },
  powerCurves: () => request<PowerCurve[]>("/api/v1/energy/power-curves/"),
  createPowerCurve: (payload: {
    turbine_model: string;
    name: string;
    air_density_ref_kg_m3?: number;
  }) =>
    request<PowerCurve>("/api/v1/energy/power-curves/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  importPowerCurve: (curveId: string, file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<{ points: number }>(`/api/v1/energy/power-curves/${curveId}/import/`, {
      method: "POST",
      body,
    });
  },
  ctCurves: () => request<CtCurve[]>("/api/v1/energy/ct-curves/"),
  createCtCurve: (payload: {
    turbine_model: string;
    name: string;
    air_density_ref_kg_m3?: number;
  }) =>
    request<CtCurve>("/api/v1/energy/ct-curves/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  importCtCurve: (curveId: string, file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<{ points: number }>(`/api/v1/energy/ct-curves/${curveId}/import/`, {
      method: "POST",
      body,
    });
  },
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
