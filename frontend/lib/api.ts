// API Client for Frontend - Aligned with Backend FastAPI

import axios, { AxiosInstance, AxiosError } from "axios";
import { 
  AuthResponse, 
  HealthData, 
  Alert, 
  HealthStatistics,
  TokenVerifyResponse,
  LoginRequest,
  RefreshTokenRequest,
  ApiResponse
} from "@/types";
import { useAuthStore } from "@/stores/authStore";

function resolveApiUrl(): string {
  const raw = (process.env.NEXT_PUBLIC_API_URL || "").trim();

  if (raw) {
    // Browsers cannot reliably call 0.0.0.0; normalize to localhost.
    return raw.replace("0.0.0.0", "localhost");
  }

  if (typeof window !== "undefined") {
    return `${window.location.protocol}//localhost:8000`;
  }

  return "http://localhost:8000";
}

const API_URL = resolveApiUrl();

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000,
    });

    // Add token to requests
    this.client.interceptors.request.use((config: any) => {
      const store = useAuthStore.getState();
      const token = store.token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle errors globally
    this.client.interceptors.response.use(
      (response: any) => response,
      (error: AxiosError<any>) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          const store = useAuthStore.getState();
          store.logout();
          
          // Only redirect if not already on login page
          if (typeof window !== "undefined" && !window.location.pathname.includes("/login")) {
            window.location.href = "/login";
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // ============ Authentication Endpoints ============

  async loginDoctor(request: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await this.client.post<AuthResponse>("/api/auth/login/doctor", request);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async loginPatient(request: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await this.client.post<AuthResponse>("/api/auth/login/patient", request);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async refreshToken(refreshTokenRequest: RefreshTokenRequest): Promise<AuthResponse> {
    try {
      const response = await this.client.post<AuthResponse>("/api/auth/refresh", refreshTokenRequest);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async verifyToken(token: string): Promise<TokenVerifyResponse> {
    try {
      const response = await this.client.post<TokenVerifyResponse>("/api/auth/verify", null, {
        params: { token },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout(): Promise<ApiResponse> {
    try {
      const response = await this.client.post<ApiResponse>("/api/auth/logout");
      return response.data;
    } catch (error) {
      // Logout should be fail-safe on the client: clear local auth even if backend is unreachable.
      const handled = this.handleError(error);
      console.warn("Logout API unreachable, proceeding with local logout:", handled.message);
      return {
        success: true,
        message: "Logged out locally",
      } as ApiResponse;
    }
  }

  // ============ Health Endpoints ============

  async getLatestVitals(): Promise<HealthData> {
    try {
      const response = await this.client.get<HealthData>("/api/health/vitals/latest");
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getVitalsHistory(limit: number = 100): Promise<HealthData[]> {
    try {
      const response = await this.client.get<HealthData[]>("/api/health/vitals/history", {
        params: { limit: Math.min(limit, 500) }, // Enforce max 500 limit
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logVitals(data: HealthData): Promise<ApiResponse> {
    try {
      const response = await this.client.post<ApiResponse>("/api/health/vitals", data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getHealthStats(): Promise<HealthStatistics> {
    try {
      const response = await this.client.get<HealthStatistics>("/api/health/statistics");
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAlerts(patientId?: string): Promise<Alert[]> {
    try {
      const response = await this.client.get<Alert[]>("/api/health/alerts", {
        params: { patient_id: patientId },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // ============ Doctor Endpoints (if available) ============

  async getDoctorProfile(): Promise<any> {
    try {
      const response = await this.client.get("/api/doctors/profile");
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getPatientList(): Promise<any[]> {
    try {
      const response = await this.client.get("/api/doctors/patients");
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async requestEmergencyAccess(payload: {
    patient_id: string;
    reason: string;
    severity: "INFO" | "WARNING" | "CRITICAL";
    expected_duration_min: number;
  }): Promise<any> {
    try {
      const response = await this.client.post("/api/doctors/emergency/request", payload);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async activateEmergencySession(sessionId: string, activationNote?: string): Promise<any> {
    try {
      const response = await this.client.post(`/api/doctors/emergency/${sessionId}/activate`, {
        activation_note: activationNote || "Activated from dashboard",
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async closeEmergencySession(sessionId: string, closureNote: string, outcome: string = "UNKNOWN"): Promise<any> {
    try {
      const response = await this.client.post(`/api/doctors/emergency/${sessionId}/close`, {
        closure_note: closureNote,
        outcome,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getEmergencySessionStatus(sessionId: string): Promise<any> {
    try {
      const response = await this.client.get(`/api/doctors/emergency/${sessionId}/status`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getPatientAccessHistory(patientId: string, limit: number = 100): Promise<any> {
    try {
      const response = await this.client.get(`/api/audit/patient-access/${patientId}`, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async emergencyAccess(patientId: string, reason?: string): Promise<any> {
    // Backward-compatible wrapper used by older UI code.
    const request = await this.requestEmergencyAccess({
      patient_id: patientId,
      reason: reason || "Emergency access",
      severity: "CRITICAL",
      expected_duration_min: 30,
    });

    if (!request?.success || !request?.session_id) {
      return request;
    }

    return this.activateEmergencySession(request.session_id);
  }

  // ============ Patient Endpoints ============

  async getPatientRecord(patientId: string, accessType?: "NORMAL" | "EMERGENCY"): Promise<any> {
    try {
      const response = await this.client.get(`/api/patients/${patientId}`, {
        params: accessType ? { access_type: accessType } : undefined,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getPatientVitals(
    patientId: string,
    limit: number = 100,
    accessType?: "NORMAL" | "EMERGENCY"
  ): Promise<HealthData[]> {
    try {
      const response = await this.client.get(`/api/patients/${patientId}/vitals`, {
        params: {
          limit: Math.min(limit, 500),
          ...(accessType ? { access_type: accessType } : {}),
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async exportPatientData(patientId: string): Promise<any> {
    try {
      const response = await this.client.post(`/api/patients/${patientId}/export`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // ============ Doctor Information Endpoints ============

  async getDoctorInfo(address: string): Promise<any> {
    try {
      const response = await this.client.get(`/api/doctors/${address}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAccessLogs(doctorAddress: string, limit: number = 100): Promise<any[]> {
    try {
      const response = await this.client.get(`/api/doctors/${doctorAddress}/access-logs`, {
        params: { limit: Math.min(limit, 500) },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAssignedPatients(doctorAddress: string): Promise<any> {
    try {
      const response = await this.client.get(`/api/doctors/${doctorAddress}/assigned-patients`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logPatientAccess(
    doctorAddress: string,
    patientId: string,
    accessType: string = "NORMAL",
    reason: string = ""
  ): Promise<any> {
    try {
      const response = await this.client.post(
        `/api/doctors/${doctorAddress}/access-patient/${patientId}`,
        { access_type: accessType, reason }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async requestAccessKey(): Promise<{ success: boolean; key?: string; message?: string }> {
    try {
      const response = await this.client.post("/api/auth/request-key");
      return response.data;
    } catch (error) {
      return { success: false, message: "An error occurred while requesting an access key." };
    }
  }

  // ============ Generic HTTP Methods ============

  async get(url: string, config?: any): Promise<any> {
    try {
      const response = await this.client.get(url, config);
      return response;
    } catch (error: any) {
      console.error(`GET ${url} error:`, error);
      if (axios.isAxiosError(error)) {
        console.error(`Response status: ${error.response?.status}`, error.response?.data);
      }
      throw this.handleError(error);
    }
  }

  async post(url: string, data?: any, config?: any): Promise<any> {
    try {
      const response = await this.client.post(url, data, config);
      return response;
    } catch (error: any) {
      console.error(`POST ${url} error:`, error);
      if (axios.isAxiosError(error)) {
        console.error(`Response status: ${error.response?.status}`, error.response?.data);
      }
      throw this.handleError(error);
    }
  }

  async put(url: string, data?: any, config?: any): Promise<any> {
    try {
      const response = await this.client.put(url, data, config);
      return response;
    } catch (error: any) {
      console.error(`PUT ${url} error:`, error);
      if (axios.isAxiosError(error)) {
        console.error(`Response status: ${error.response?.status}`, error.response?.data);
      }
      throw this.handleError(error);
    }
  }

  async patch(url: string, data?: any, config?: any): Promise<any> {
    try {
      const response = await this.client.patch(url, data, config);
      return response;
    } catch (error: any) {
      console.error(`PATCH ${url} error:`, error);
      if (axios.isAxiosError(error)) {
        console.error(`Response status: ${error.response?.status}`, error.response?.data);
      }
      throw this.handleError(error);
    }
  }

  async delete(url: string, config?: any): Promise<any> {
    try {
      const response = await this.client.delete(url, config);
      return response;
    } catch (error: any) {
      console.error(`DELETE ${url} error:`, error);
      if (axios.isAxiosError(error)) {
        console.error(`Response status: ${error.response?.status}`, error.response?.data);
      }
      throw this.handleError(error);
    }
  }

  // ============ Utility Methods ============

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      if (!error.response) {
        return new Error("Network error: unable to reach backend API. Check that backend is running on localhost:8000.");
      }

      const status = error.response?.status;
      const data = error.response?.data;
      const rawDetail = data?.detail ?? data?.message ?? "Unknown error";
      const detail =
        typeof rawDetail === "string"
          ? rawDetail
          : rawDetail?.message || JSON.stringify(rawDetail);
      const detailCode =
        typeof rawDetail === "object" && rawDetail !== null ? rawDetail.code : undefined;

      switch (status) {
        case 400:
          return new Error(`Invalid request: ${detail}`);
        case 401:
          return new Error("Unauthorized - please login again");
        case 403:
          if (detailCode === "EMERGENCY_SESSION_REQUIRED") {
            return new Error("Emergency session required before accessing this patient");
          }
          return new Error(`Access forbidden: ${detail}`);
        case 404:
          return new Error("Resource not found");
        case 500:
          return new Error("Server error - please try again later");
        default:
          return new Error(detail || "Request failed");
      }
    }

    if (error instanceof Error) {
      return error;
    }

    return new Error("An unexpected error occurred");
  }

  // Reset client (for logout)
  reset(): void {
    this.client.defaults.headers.common["Authorization"] = "";
  }
}

//  Singleton instance
let apiClientInstance: ApiClient | null = null;

export function getApiClient(): ApiClient {
  if (!apiClientInstance) {
    apiClientInstance = new ApiClient();
  }
  return apiClientInstance;
}

export function resetApiClient(): void {
  if (apiClientInstance) {
    apiClientInstance.reset();
  }
}

/**
 * Logout helper function (for backwards compatibility)
 */
export async function logout(): Promise<void> {
  const client = getApiClient();
  const store = useAuthStore.getState();
  
  try {
    await client.logout();
  } catch (error) {
    console.error("Logout API call failed:", error);
  } finally {
    await store.logout();
  }
}

export const apiClient = new ApiClient();
