// Main Dashboard Page

import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { Header } from "@/components/Header";
import { VitalsCard } from "@/components/VitalsCard";
import { HealthCharts } from "@/components/HealthCharts";
import { AlertsList } from "@/components/AlertsList";
import { useAuthStore } from "@/lib/auth";
import { apiClient } from "@/lib/api";
import { HealthData, Alert } from "@/types";
import toast from "react-hot-toast";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, role, userAddress } = useAuthStore();
  const [vitals, setVitals] = useState<HealthData | null>(null);
  const [history, setHistory] = useState<HealthData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [emergencyPatientId, setEmergencyPatientId] = useState("");
  const [emergencyPatientData, setEmergencyPatientData] = useState<any>(null);

  const handleEmergencyAccess = async () => {
    if (!emergencyPatientId) {
      toast.error("Please enter a patient ID.");
      return;
    }
    try {
      // In a real scenario, a secure key would be generated and used.
      // For this version, we'll send a placeholder key.
      const randomKey = "emergency_key_" + Math.random().toString(36).substring(2);
      const response = await apiClient.emergencyAccess(emergencyPatientId, randomKey);
      if (response.data.success) {
        setEmergencyPatientData(response.data.patient_data);
        toast.success("Emergency access granted.");
      } else {
        toast.error("Emergency access failed.");
      }
    } catch (error) {
      console.error("Emergency access error:", error);
      toast.error("Failed to get emergency access.");
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    const fetchData = async () => {
      try {
        const [vitalsRes, historyRes, alertsRes, statsRes] = await Promise.all([
          apiClient.getLatestVitals(),
          apiClient.getVitalsHistory(100),
          apiClient.getAlerts(),
          apiClient.getHealthStats(),
        ]);

        setVitals(vitalsRes.data);
        setHistory(historyRes.data);
        setAlerts(alertsRes.data);
        setStats(statsRes.data);
      } catch (error) {
        toast.error("Failed to load dashboard data");
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Refresh every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return null;
  }

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
              Welcome, {role}
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
              {role === "DOCTOR" && (
                <div className="bg-card p-6 rounded-lg shadow-md">
                  <h2 className="text-2xl font-bold text-foreground mb-4">Emergency Access</h2>
                  <div className="flex space-x-4">
                    <input
                      type="text"
                      placeholder="Enter Patient ID"
                      className="flex-grow p-2 border rounded-md bg-background text-foreground"
                      value={emergencyPatientId}
                      onChange={(e) => setEmergencyPatientId(e.target.value)}
                    />
                    <button
                      onClick={handleEmergencyAccess}
                      className="bg-primary text-primary-foreground px-4 py-2 rounded-md"
                    >
                      Generate & Access
                    </button>
                  </div>
                  {emergencyPatientData && (
                    <div className="mt-4">
                      <h3 className="text-xl font-bold">Patient: {emergencyPatientData.name}</h3>
                      <VitalsCard data={emergencyPatientData.vitals} isLive={false} />
                    </div>
                  )}
                </div>
              )}

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
                            {new Date(vital.timestamp).toLocaleTimeString()}
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
            </div>
          )}
        </div>
      </div>
    </>
  );
}
