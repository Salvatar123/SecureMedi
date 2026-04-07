// TypeScript Type Definitions

export interface HealthData {
  heart_rate: number;
  temperature: number;
  spo2: number;
  timestamp: string;
  status: "NORMAL" | "WARNING" | "CRITICAL";
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
  access_logs: string[];
}

export interface DoctorInfo {
  address: string;
  name?: string;
  specialization?: string;
  created_at: string;
}

export interface AccessLog {
  doctor_address: string;
  patient_id: string;
  access_type: string;
  timestamp: string;
  reason?: string;
}
