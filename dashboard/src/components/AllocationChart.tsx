import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import type { ChartPoint } from "../types/dashboard";

const COLORS = ["#0f766e", "#0284c7", "#7c3aed", "#ea580c", "#64748b"];

interface AllocationChartProps {
  data: ChartPoint[];
}

export function AllocationChart({ data }: AllocationChartProps) {
  const chartData = data.map((point) => ({
    name: point.label,
    value: Number(point.value),
  }));

  return (
    <div className="chart-card">
      <h3>Asset Allocation</h3>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            innerRadius={60}
            outerRadius={95}
            paddingAngle={2}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={entry.name}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
