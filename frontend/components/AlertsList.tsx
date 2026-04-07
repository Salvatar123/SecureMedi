// Alerts Component

import React from "react";
import { Alert } from "@/types";
import { ExclamationTriangleIcon, CheckCircleIcon } from "@heroicons/react/16/solid";

interface AlertsProps {
  alerts: Alert[];
}

export const AlertsList: React.FC<AlertsProps> = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="metric-card">
        <div className="flex items-center space-x-2">
          <CheckCircleIcon className="w-5 h-5 text-success" />
          <span className="text-sm text-foreground/70">No active alerts</span>
        </div>
      </div>
    );
  }

  const getSeverityColor = (severity: number) => {
    if (severity >= 4) return "bg-danger/20 border-danger/50";
    if (severity >= 3) return "bg-warning/20 border-warning/50";
    return "bg-info/20 border-info/50";
  };

  const getSeverityBadge = (severity: number) => {
    if (severity >= 4) return <span className="bg-danger text-white px-2 py-1 rounded text-xs font-semibold">CRITICAL</span>;
    if (severity >= 3) return <span className="bg-warning text-white px-2 py-1 rounded text-xs font-semibold">WARNING</span>;
    return <span className="bg-info text-white px-2 py-1 rounded text-xs font-semibold">INFO</span>;
  };

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)} space-y-2`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ExclamationTriangleIcon className="w-5 h-5 text-warning" />
              <span className="font-semibold text-sm">{alert.alert_type}</span>
            </div>
            {getSeverityBadge(alert.severity)}
          </div>
          <p className="text-sm text-foreground/80">{alert.message}</p>
          <p className="text-xs text-foreground/50">
            {new Date(alert.timestamp).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
};
