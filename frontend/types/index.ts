// TypeScript Type Definitions - Aligned with Backend

// ============ Auth Types ============

export type UserRole = "DOCTOR" | "PATIENT" | "ADMIN";

export interface LoginRequest {
  address: string;
  key: string;
}

export interface AuthResponse {
  success: boolean;
  token?: string;
  refresh_token?: string;
  role?: UserRole;
  user_address?: string;
  user_name?: string;
  message: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface TokenVerifyResponse {
  valid: boolean;
  address?: string;
  role?: UserRole;
  expires_at?: number;
  error?: string;
}

// ============ Health Data Types ============

export interface HealthData {
  heart_rate: number;
  temperature: number;
  spo2: number;
  timestamp?: string;
  status?: "NORMAL" | "WARNING" | "CRITICAL";
}

export interface Alert {
  id: string;
  patient_id: string;
  alert_type: string;
  message: string;
  severity: number;
  timestamp: string;
  resolved: boolean;
}

export interface HealthStatistics {
  average_heart_rate: number;
  average_temperature: number;
  average_spo2: number;
  total_alerts: number;
  critical_alerts: number;
  warning_alerts: number;
  last_updated: string;
}

// ============ Patient Types ============

export interface PatientInfo {
  patient_id: string;
  name?: string;
  age?: number;
  contact?: string;
  emergency_contact?: string;
  created_at: string;
}

export interface PatientRecord {
  patient_info: PatientInfo;
  latest_vitals?: HealthData;
  health_history: HealthData[];
  active_alerts: Alert[];
  access_logs: AccessLog[];
}

// ============ Doctor Types ============

export interface DoctorInfo {
  address: string;
  name?: string;
  specialization?: string;
  hospital?: string;
  created_at: string;
}

// ============ Audit Types ============

export interface AccessLog {
  doctor_address: string;
  patient_id: string;
  access_type: string;
  timestamp: string;
  reason?: string;
}

// ============ API Response Types ============

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}
