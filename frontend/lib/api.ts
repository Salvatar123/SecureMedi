// API Client for Frontend

import axios, { AxiosInstance, AxiosError } from "axios";
import Cookie from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add token to requests
    this.client.interceptors.request.use((config: any) => {
      const token = Cookie.get("auth_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle errors globally
    this.client.interceptors.response.use(
      (response: any) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Clear auth
          Cookie.remove("auth_token");
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async loginDoctor(address: string, key: string) {
    return this.client.post("/api/auth/login/doctor", { address, key });
  }

  async loginPatient(patientId: string, privateKey: string) {
    return this.client.post("/api/auth/login/patient", {
      address: patientId,
      key: privateKey,
    });
  }

  // Health endpoints
  async getLatestVitals() {
    return this.client.get("/api/health/vitals/latest");
  }

  async getVitalsHistory(limit = 100) {
    return this.client.get("/api/health/vitals/history", { params: { limit } });
  }

  async getHealthStats() {
    return this.client.get("/api/health/statistics");
  }

  async getAlerts(patientId?: string) {
    return this.client.get("/api/health/alerts", { params: { patient_id: patientId } });
  }

  // Patient endpoints
  async getPatientRecord(patientId: string) {
    return this.client.get(`/api/patients/${patientId}`);
  }

  async getPatientVitals(patientId: string, limit = 100) {
    return this.client.get(`/api/patients/${patientId}/vitals`, { params: { limit } });
  }

  async exportPatientData(patientId: string) {
    return this.client.post(`/api/patients/${patientId}/export`);
  }

  // Doctor endpoints
  async getDoctorInfo(address: string) {
    return this.client.get(`/api/doctors/${address}`);
  }

  async getAccessLogs(doctorAddress: string, limit = 100) {
    return this.client.get(`/api/doctors/${doctorAddress}/access-logs`, { params: { limit } });
  }

  async logPatientAccess(doctorAddress: string, patientId: string, accessType = "NORMAL", reason = "") {
    return this.client.post(
      `/api/doctors/${doctorAddress}/access-patient/${patientId}`,
      { access_type: accessType, reason }
    );
  }

  async emergencyAccess(patientId: string, key: string) {
    return this.client.post("/api/doctors/emergency-access", { patient_id: patientId, key });
  }
}

export const apiClient = new ApiClient();
