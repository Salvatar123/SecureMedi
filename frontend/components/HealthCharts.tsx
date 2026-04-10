// Health Charts Component

import React from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { HealthData } from "@/types";

interface ChartsProps {
  data: HealthData[];
}

export const HealthCharts: React.FC<ChartsProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="metric-card">
        <p className="text-sm text-foreground/50">No data to display</p>
      </div>
    );
  }

  const chartData = data
    .slice()
    .reverse()
    .map((d) => ({
      time: new Date(d.timestamp ?? new Date().toISOString()).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      heart_rate: d.heart_rate,
      temperature: (d.temperature * 10).toFixed(0),
      spo2: d.spo2,
    }));

  return (
    <div className="space-y-6">
      <div className="metric-card">
        <h3 className="font-semibold text-lg mb-4">Heart Rate Trend</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
              }}
            />
            <Line
              type="monotone"
              dataKey="heart_rate"
              stroke="#f43f5e"
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="metric-card">
        <h3 className="font-semibold text-lg mb-4">Temperature Trend</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
              }}
            />
            <Line
              type="monotone"
              dataKey="temperature"
              stroke="#f59e0b"
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="metric-card">
        <h3 className="font-semibold text-lg mb-4">SpO₂ Levels</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
              }}
            />
            <Bar dataKey="spo2" fill="#06b6d4" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
