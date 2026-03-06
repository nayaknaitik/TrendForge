const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  token?: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async request<T>(
    endpoint: string,
    options: FetchOptions = {}
  ): Promise<T> {
    const { token, ...fetchOptions } = options;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(fetchOptions.headers as Record<string, string>),
    };

    const authToken = token || this.token;
    if (authToken) {
      headers["Authorization"] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        error.detail || error.message || "Request failed"
      );
    }

    if (response.status === 204) return {} as T;
    return response.json();
  }

  // Auth
  async login(email: string, password: string) {
    return this.request<{ access_token: string; refresh_token: string }>(
      "/api/v1/auth/login",
      { method: "POST", body: JSON.stringify({ email, password }) }
    );
  }

  async register(email: string, password: string, full_name: string) {
    return this.request<{ id: string; email: string }>(
      "/api/v1/auth/register",
      { method: "POST", body: JSON.stringify({ email, password, full_name }) }
    );
  }

  // Brands
  async getBrands() {
    return this.request<{ brands: any[]; total: number }>("/api/v1/brands");
  }

  async createBrand(data: any) {
    return this.request<any>("/api/v1/brands", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateBrand(id: string, data: any) {
    return this.request<any>(`/api/v1/brands/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteBrand(id: string) {
    return this.request<void>(`/api/v1/brands/${id}`, { method: "DELETE" });
  }

  // Trends
  async getTrends(params?: Record<string, any>) {
    const query = params
      ? "?" + new URLSearchParams(params).toString()
      : "";
    return this.request<{ trends: any[]; total: number }>(
      `/api/v1/trends${query}`
    );
  }

  async refreshTrends() {
    return this.request<{ message: string; new_trends: number }>(
      "/api/v1/trends/refresh",
      { method: "POST" }
    );
  }

  async matchTrendsToBrand(brandId: string) {
    return this.request<any[]>(`/api/v1/trends/match/${brandId}`);
  }

  // Campaigns
  async generateCampaign(data: {
    brand_id: string;
    trend_id: string;
    target_platforms?: string[];
    objective?: string;
  }) {
    return this.request<any>("/api/v1/campaigns/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getCampaigns(params?: Record<string, any>) {
    const query = params
      ? "?" + new URLSearchParams(params).toString()
      : "";
    return this.request<{ campaigns: any[]; total: number }>(
      `/api/v1/campaigns${query}`
    );
  }

  async getCampaign(id: string) {
    return this.request<any>(`/api/v1/campaigns/${id}`);
  }

  async deleteCampaign(id: string) {
    return this.request<void>(`/api/v1/campaigns/${id}`, { method: "DELETE" });
  }

  async exportCampaign(id: string, format: "json" | "csv" | "pdf" = "json") {
    return this.request<any>(
      `/api/v1/campaigns/${id}/export?export_format=${format}`,
      { method: "POST" }
    );
  }
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

export const api = new ApiClient(API_BASE);
