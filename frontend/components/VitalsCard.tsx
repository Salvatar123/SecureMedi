// Vitals Card Component

import React from "react";
import { HealthData } from "@/types";
import { HeartIcon, FireIcon, SparklesIcon } from "@heroicons/react/16/solid";

interface VitalsCardProps {
  data: HealthData | null;
  isLive?: boolean;
}

export const VitalsCard: React.FC<VitalsCardProps> = ({ data, isLive = true }: VitalsCardProps) => {
  if (!data) {
    return (
      <div className="metric-card">
        <p className="text-sm text-foreground/50">No vitals available</p>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "CRITICAL":
        return "text-danger";
      case "WARNING":
        return "text-warning";
      case "NORMAL":
        return "text-success";
      default:
        return "text-foreground/50";
    }
  };

  return (
    <div className="metric-card space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-lg">Current Vitals</h3>
        {isLive && (
          <span className="flex items-center space-x-1 text-xs text-success animate-pulse-glow">
            <span className="w-2 h-2 bg-success rounded-full"></span>
            <span>LIVE</span>
          </span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-sm text-foreground/70">
            <HeartIcon className="w-4 h-4 text-danger" />
            <span>Heart Rate</span>
          </div>
          <p className="text-2xl font-bold">{data.heart_rate}</p>
          <p className="text-xs text-foreground/50">bpm</p>
        </div>

        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-sm text-foreground/70">
            <FireIcon className="w-4 h-4 text-warning" />
            <span>Temperature</span>
          </div>
          <p className="text-2xl font-bold">{data.temperature.toFixed(1)}</p>
          <p className="text-xs text-foreground/50">°C</p>
        </div>

        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-sm text-foreground/70">
            <SparklesIcon className="w-4 h-4 text-info" />
            <span>SpO₂</span>
          </div>
          <p className="text-2xl font-bold">{data.spo2}</p>
          <p className="text-xs text-foreground/50">%</p>
        </div>
      </div>

      <div className="pt-2 border-t border-border flex items-center justify-between">
        <span className={`text-sm font-semibold ${getStatusColor(data.status)}`}>
          {data.status}
        </span>
        <span className="text-xs text-foreground/50">
          {new Date(data.timestamp).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
};
