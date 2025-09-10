import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const TIMEFRAMES = {
  "1D": { label: "1D", days: 1 },
  "1M": { label: "1M", days: 30 },
  ALL: { label: "All", days: null },
};

export function PriceGraph(props) {
  const { data, formatLabel } = props;

  return (
    <div data-testid="recharts-responsive-container" className="bg-white rounded-xl shadow p-4 w-full">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid vertical={false} horizontal={true} />
          <XAxis dataKey="timestamp" tickFormatter={formatLabel} />
          <YAxis
            domain={["auto", "auto"]}
            mirror={true}
            orientation="right"
            axisLine={false}
            tickLine={false}
            padding={{ bottom: 10 }}
          />
          <Tooltip labelFormatter={formatLabel} />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PriceGraph;
