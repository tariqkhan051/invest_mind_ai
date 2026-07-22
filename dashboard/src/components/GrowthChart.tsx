import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ChartPoint } from "../types/dashboard";

interface GrowthChartProps {
  data: ChartPoint[];
}

export function GrowthChart({ data }: GrowthChartProps) {
  const chartData = data.map((point) => ({
    date: point.label,
    value: Number(point.value),
  }));

  return (
    <div className="chart-card">
      <h3>Portfolio Growth</h3>
      {chartData.length === 0 ? (
        <p className="empty-state">No snapshot history yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value: number) =>
                `PKR ${value.toLocaleString(undefined, {
                  maximumFractionDigits: 0,
                })}`
              }
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#0f766e"
              strokeWidth={3}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
