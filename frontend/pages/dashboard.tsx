// Main Dashboard Page - Aligned with Backend API

import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { Header } from "@/components/Header";
import { VitalsCard } from "@/components/VitalsCard";
import { HealthCharts } from "@/components/HealthCharts";
import { AlertsList } from "@/components/AlertsList";
import { withProtectedRoute } from "@/lib/protectedRoute";
import { useAuthStore } from "@/stores/authStore";
import { getApiClient } from "@/lib/api";
import { HealthData, Alert, HealthStatistics } from "@/types";
import toast from "react-hot-toast";

interface AssignedPatient {
  id: string;
  patient_id: string;
  name?: string;
  email?: string;
  status?: string;
  wallet_address?: string;
  assigned_at?: string;
}

function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, userRole, user } = useAuthStore();
  const [vitals, setVitals] = useState<HealthData | null>(null);
  const [history, setHistory] = useState<HealthData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<HealthStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [emergencyPatientId, setEmergencyPatientId] = useState("");
  const [emergencyReason, setEmergencyReason] = useState("");
  const [emergencySeverity, setEmergencySeverity] = useState<"INFO" | "WARNING" | "CRITICAL">("CRITICAL");
  const [emergencyDurationMin, setEmergencyDurationMin] = useState(30);
  const [activeEmergencySession, setActiveEmergencySession] = useState<any>(null);
  const [emergencyCloseNote, setEmergencyCloseNote] = useState("");
  const [assignedPatients, setAssignedPatients] = useState<AssignedPatient[]>([]);
  const [reportPatientIdInput, setReportPatientIdInput] = useState("");
  const [reportPatientId, setReportPatientId] = useState("");
  const [reportAccessLockedMessage, setReportAccessLockedMessage] = useState<string | null>(null);
  const effectiveReportPatientId =
    userRole === "DOCTOR"
      ? reportPatientId.trim()
      : "";

  const computeStatsFromHistory = (records: HealthData[]): HealthStatistics => {
    if (!records.length) {
      return {
        average_heart_rate: 0,
        average_temperature: 0,
        average_spo2: 0,
        total_alerts: 0,
        critical_alerts: 0,
        warning_alerts: 0,
        last_updated: new Date().toISOString(),
      };
    }

    const total = records.length;
    const average_heart_rate = records.reduce((sum, r) => sum + r.heart_rate, 0) / total;
    const average_temperature = records.reduce((sum, r) => sum + r.temperature, 0) / total;
    const average_spo2 = records.reduce((sum, r) => sum + r.spo2, 0) / total;
    const critical_alerts = records.filter((r) => r.status === "CRITICAL").length;
    const warning_alerts = records.filter((r) => r.status === "WARNING").length;

    return {
      average_heart_rate: Number(average_heart_rate.toFixed(1)),
      average_temperature: Number(average_temperature.toFixed(1)),
      average_spo2: Number(average_spo2.toFixed(1)),
      total_alerts: critical_alerts + warning_alerts,
      critical_alerts,
      warning_alerts,
      last_updated: new Date().toISOString(),
    };
  };

  const handleEmergencyAccess = async () => {
    if (!emergencyPatientId) {
      toast.error("Please enter a patient ID.");
      return;
    }

    if (emergencyReason.trim().length < 15) {
      toast.error("Emergency reason must be at least 15 characters.");
      return;
    }

    const trimmedPatientId = emergencyPatientId.trim();

    // If patient is already assigned, bypass emergency mode and open regular report.
    const isAssignedPatient = assignedPatients.some(
      (patient) => patient.patient_id?.trim().toLowerCase() === trimmedPatientId.toLowerCase()
    );
    if (isAssignedPatient) {
      setReportPatientIdInput(trimmedPatientId);
      setReportPatientId(trimmedPatientId);
      setReportAccessLockedMessage(null);
      toast.success("Patient is already assigned. Opened normal report access.");
      return;
    }
    
    try {
      const apiClient = getApiClient();
      const requestResponse = await apiClient.requestEmergencyAccess({
        patient_id: trimmedPatientId,
        reason: emergencyReason.trim(),
        severity: emergencySeverity,
        expected_duration_min: emergencyDurationMin,
      });

      if (!requestResponse?.success || !requestResponse?.session_id) {
        toast.error(requestResponse?.message || "Emergency request failed.");
        return;
      }

      const activateResponse = await apiClient.activateEmergencySession(
        requestResponse.session_id,
        "Activated from dashboard"
      );

      if (!activateResponse?.success) {
        toast.error(activateResponse?.message || "Emergency activation failed.");
        return;
      }

      setActiveEmergencySession(activateResponse);
      setReportPatientIdInput(trimmedPatientId);
      setReportPatientId(trimmedPatientId);
      setReportAccessLockedMessage(null);
      toast.success("Emergency session activated.");
    } catch (error: any) {
      console.error("Emergency access error:", error);
      const message = error?.message || "Failed to get emergency access.";
      if (message.includes("already assigned")) {
        setReportPatientIdInput(trimmedPatientId);
        setReportPatientId(trimmedPatientId);
        setReportAccessLockedMessage(null);
        toast.success("Patient is already assigned. Opened normal report access.");
        return;
      }
      toast.error(message);
    }
  };

  const handleCloseEmergencySession = async () => {
    if (!activeEmergencySession?.session_id) {
      return;
    }

    if (emergencyCloseNote.trim().length < 8) {
      toast.error("Please provide a closure note (minimum 8 characters).");
      return;
    }

    try {
      const apiClient = getApiClient();
      const response = await apiClient.closeEmergencySession(
        activeEmergencySession.session_id,
        emergencyCloseNote.trim(),
        "COMPLETED"
      );

      if (response?.success) {
        setActiveEmergencySession(null);
        setEmergencyCloseNote("");
        toast.success("Emergency session closed.");
      } else {
        toast.error(response?.message || "Failed to close emergency session.");
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to close emergency session.");
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    const fetchData = async () => {
      try {
        const apiClient = getApiClient();

        const assignedPatientsPromise = user?.address
          ? apiClient.getAssignedPatients(user.address).catch(() => ({ success: false, data: [] }))
          : Promise.resolve({ success: false, data: [] });

        // For doctors, only load report data when a patient ID is explicitly selected.
        if (userRole === "DOCTOR" && !effectiveReportPatientId) {
          const assignedPatientsData = await assignedPatientsPromise;
          setVitals(null);
          setHistory([]);
          setAlerts([]);
          setStats(null);
          if (assignedPatientsData?.success) {
            setAssignedPatients(assignedPatientsData.data || []);
          } else {
            setAssignedPatients([]);
          }
          return;
        }

        const reportId = effectiveReportPatientId;
        const historyPromise = userRole === "DOCTOR"
          ? apiClient.getPatientVitals(reportId, 100).catch((err: any) => {
              const msg = err?.message || "";
              if (msg.includes("Emergency session required")) {
                setReportAccessLockedMessage("Emergency session required before accessing this patient report.");
                setReportPatientId("");
                return [];
              }
              toast.error(msg || "Unable to load patient vitals right now.");
              return [];
            })
          : apiClient.getVitalsHistory(100).catch(() => []);

        const [historyData, alertsData, assignedPatientsData] = await Promise.all([
          historyPromise,
          apiClient.getAlerts(userRole === "DOCTOR" ? reportId : undefined).catch(() => []),
          assignedPatientsPromise,
        ]);

        if (userRole === "DOCTOR" && reportId && Array.isArray(historyData)) {
          setReportAccessLockedMessage(null);
        }

        const safeHistory = historyData || [];
        setHistory(safeHistory);
        setAlerts(alertsData || []);
        setVitals(
          safeHistory.length
            ? safeHistory[safeHistory.length - 1]
            : {
                heart_rate: 72,
                temperature: 36.6,
                spo2: 98,
                status: "NORMAL",
              }
        );
        setStats(computeStatsFromHistory(safeHistory));

        if (assignedPatientsData?.success) {
          setAssignedPatients(assignedPatientsData.data || []);
        } else {
          setAssignedPatients([]);
        }
      } catch (error: any) {
        console.error("Dashboard data fetch error:", error);
        if ((error?.message || "").includes("Emergency session required")) {
          setReportAccessLockedMessage("Emergency session required before accessing this patient report.");
          toast.error("Emergency session required to access this patient.");
          setReportPatientId("");
        } else {
          toast.error("Failed to load dashboard data");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Refresh every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [isAuthenticated, router, user?.address, userRole, reportPatientId]);

  useEffect(() => {
    if (!activeEmergencySession?.session_id) {
      return;
    }

    let mounted = true;
    const apiClient = getApiClient();

    const pollStatus = async () => {
      try {
        const status = await apiClient.getEmergencySessionStatus(activeEmergencySession.session_id);
        if (!mounted) {
          return;
        }

        if (status?.success) {
          setActiveEmergencySession(status);
          if (status.status === "EXPIRED" || status.seconds_remaining === 0) {
            toast.error("Emergency session expired.");
          }
        }
      } catch {
        // Ignore transient polling errors.
      }
    };

    const interval = setInterval(pollStatus, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [activeEmergencySession?.session_id]);

  return (
    <>
      <Head>
        <title>Dashboard - SecureMedi</title>
      </Head>

      <Header />

      <div className="min-h-screen bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header Section */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-foreground mb-2">
              Welcome, {userRole}
            </h1>
            <p className="text-foreground/60">Real-time health monitoring dashboard</p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="space-y-8">
              {/* Emergency Access for Doctors */}
              {userRole === "DOCTOR" && (
                <div className="bg-card p-6 rounded-lg shadow-md">
                  <h2 className="text-2xl font-bold text-foreground mb-4">Emergency Access</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <input
                      type="text"
                      placeholder="Enter Patient ID"
                      className="p-2 border rounded-md bg-background text-foreground"
                      value={emergencyPatientId}
                      onChange={(e) => setEmergencyPatientId(e.target.value)}
                    />
                    <select
                      className="p-2 border rounded-md bg-background text-foreground"
                      value={emergencySeverity}
                      onChange={(e) => setEmergencySeverity(e.target.value as "INFO" | "WARNING" | "CRITICAL")}
                    >
                      <option value="INFO">INFO</option>
                      <option value="WARNING">WARNING</option>
                      <option value="CRITICAL">CRITICAL</option>
                    </select>
                    <input
                      type="number"
                      min={5}
                      max={120}
                      className="p-2 border rounded-md bg-background text-foreground"
                      value={emergencyDurationMin}
                      onChange={(e) => setEmergencyDurationMin(Math.max(5, Math.min(120, Number(e.target.value) || 30)))}
                      placeholder="Expected duration (minutes)"
                    />
                    <button
                      onClick={handleEmergencyAccess}
                      className="bg-primary text-primary-foreground px-4 py-2 rounded-md"
                    >
                      Activate Emergency Session
                    </button>
                  </div>
                  <textarea
                    placeholder="Clinical reason (required, minimum 15 characters)"
                    className="w-full mt-4 p-2 border rounded-md bg-background text-foreground"
                    rows={3}
                    value={emergencyReason}
                    onChange={(e) => setEmergencyReason(e.target.value)}
                  />
                  {activeEmergencySession?.session_id && (
                    <div className="mt-4 p-4 rounded-md border border-red-300 bg-red-50 text-red-800">
                      <p className="font-semibold">Emergency Session Active</p>
                      <p className="text-sm">Session ID: {activeEmergencySession.session_id}</p>
                      <p className="text-sm">Patient: {activeEmergencySession.patient_id}</p>
                      <p className="text-sm">Time Remaining: {Math.floor((activeEmergencySession.seconds_remaining || 0) / 60)}m {(activeEmergencySession.seconds_remaining || 0) % 60}s</p>
                      <div className="flex gap-2 mt-3">
                        <input
                          type="text"
                          className="flex-grow p-2 border rounded-md bg-background text-foreground"
                          placeholder="Closure note"
                          value={emergencyCloseNote}
                          onChange={(e) => setEmergencyCloseNote(e.target.value)}
                        />
                        <button
                          onClick={handleCloseEmergencySession}
                          className="bg-red-600 text-white px-4 py-2 rounded-md"
                        >
                          Close Session
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {userRole === "DOCTOR" && (
                <div className="bg-card p-6 rounded-lg shadow-md">
                  <h2 className="text-2xl font-bold text-foreground mb-4">Patient Report Access</h2>
                  <p className="text-sm text-foreground/70 mb-4">
                    Enter a Patient ID to unlock and view report sections (vitals, trends, alerts, and statistics).
                  </p>
                  <div className="flex gap-3">
                    <input
                      type="text"
                      placeholder="Enter Patient ID"
                      value={reportPatientIdInput}
                      onChange={(e) => setReportPatientIdInput(e.target.value)}
                      className="flex-grow p-2 border rounded-md bg-background text-foreground"
                    />
                    <button
                      onClick={() => {
                        const value = reportPatientIdInput.trim();
                        if (!value) {
                          toast.error("Please enter a patient ID");
                          return;
                        }
                        setReportAccessLockedMessage(null);
                        setReportPatientId(value);
                        toast.success(`Report loaded for ${value}`);
                      }}
                      className="bg-primary text-primary-foreground px-4 py-2 rounded-md"
                    >
                      View Report
                    </button>
                    <button
                      onClick={() => {
                        setReportPatientId("");
                        setReportPatientIdInput("");
                      }}
                      className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md"
                    >
                      Clear
                    </button>
                  </div>
                  {effectiveReportPatientId && (
                    <p className="text-sm text-foreground/70 mt-3">
                      Showing report for Patient ID: <strong>{effectiveReportPatientId}</strong>
                    </p>
                  )}
                  {reportAccessLockedMessage && (
                    <p className="text-sm text-red-600 mt-3">{reportAccessLockedMessage}</p>
                  )}
                </div>
              )}

              {userRole === "DOCTOR" && (
                <div className="metric-card">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Assigned Patients</h3>
                    <span className="text-sm text-foreground/60">{assignedPatients.length} total</span>
                  </div>
                  {assignedPatients.length === 0 ? (
                    <p className="text-sm text-foreground/60">No patients assigned yet.</p>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-border">
                            <th className="px-3 py-2 text-left text-foreground/70">Patient ID</th>
                            <th className="px-3 py-2 text-left text-foreground/70">Name</th>
                            <th className="px-3 py-2 text-left text-foreground/70">Email</th>
                            <th className="px-3 py-2 text-left text-foreground/70">Status</th>
                            <th className="px-3 py-2 text-left text-foreground/70">Action</th>
                          </tr>
                        </thead>
                        <tbody>
                          {assignedPatients.map((patient) => (
                            <tr key={patient.id} className="border-b border-border/50 hover:bg-border/10">
                              <td className="px-3 py-2 font-mono">{patient.patient_id}</td>
                              <td className="px-3 py-2">{patient.name || "-"}</td>
                              <td className="px-3 py-2">{patient.email || "-"}</td>
                              <td className="px-3 py-2">{patient.status || "-"}</td>
                              <td className="px-3 py-2">
                                <button
                                  onClick={() => {
                                    setEmergencyPatientId(patient.patient_id);
                                    setReportPatientIdInput(patient.patient_id);
                                    setReportPatientId(patient.patient_id);
                                  }}
                                  className="text-blue-600 hover:text-blue-800 font-medium"
                                >
                                  Open Report
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}

              {(userRole !== "DOCTOR" || effectiveReportPatientId) ? (
                <>
                  {/* Vitals Overview */}
                  <VitalsCard data={vitals} isLive={true} />

                  {/* Statistics */}
                  {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      {Object.entries(stats)
                        .slice(0, 4)
                        .map(([key, value]: [string, any]) => (
                          <div key={key} className="metric-card">
                            <p className="text-sm text-foreground/60 capitalize">{key.replace("_", " ")}</p>
                            <p className="text-2xl font-bold mt-2">{value}</p>
                          </div>
                        ))}
                    </div>
                  )}

                  {/* Alerts Section */}
                  <div>
                    <h2 className="text-2xl font-bold mb-4 text-foreground">Active Alerts</h2>
                    <AlertsList alerts={alerts} />
                  </div>

                  {/* Charts */}
                  <div>
                    <h2 className="text-2xl font-bold mb-4 text-foreground">Health Trends</h2>
                    <HealthCharts data={history} />
                  </div>

                  {/* Data Table */}
                  <div className="metric-card">
                    <h3 className="text-lg font-semibold mb-4">Recent Vitals</h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-border">
                            <th className="px-4 py-2 text-left text-foreground/70">Time</th>
                            <th className="px-4 py-2 text-left text-foreground/70">Heart Rate</th>
                            <th className="px-4 py-2 text-left text-foreground/70">Temperature</th>
                            <th className="px-4 py-2 text-left text-foreground/70">SpO₂</th>
                            <th className="px-4 py-2 text-left text-foreground/70">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {history.slice(0, 10).map((vital, idx) => (
                            <tr key={idx} className="border-b border-border/50 hover:bg-border/10">
                              <td className="px-4 py-3">
                                {new Date(vital.timestamp || new Date().toISOString()).toLocaleTimeString()}
                              </td>
                              <td className="px-4 py-3">{vital.heart_rate} bpm</td>
                              <td className="px-4 py-3">{vital.temperature.toFixed(1)}°C</td>
                              <td className="px-4 py-3">{vital.spo2}%</td>
                              <td className="px-4 py-3">
                                <span
                                  className={`px-2 py-1 rounded text-xs font-semibold ${
                                    vital.status === "CRITICAL"
                                      ? "bg-danger/20 text-danger"
                                      : vital.status === "WARNING"
                                      ? "bg-warning/20 text-warning"
                                      : "bg-success/20 text-success"
                                  }`}
                                >
                                  {vital.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              ) : (
                <div className="metric-card">
                  <h3 className="text-lg font-semibold mb-2">Patient Report Locked</h3>
                  <p className="text-sm text-foreground/60">
                    Enter a Patient ID in the "Patient Report Access" section above to view the report.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default withProtectedRoute(DashboardPage, { requiredRole: ["DOCTOR", "PATIENT"] });
