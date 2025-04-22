import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { GraphStat } from './rating_chart';

type ChartRow = {
  metric: string;
} & {
  [key: `${string}_low`]: number;
} & {
  [key: `${string}_range`]: number;
};


type Props = {
  data: GraphStat[];
}

export default function ConfidenceIntervalChart({ data }: Props) {
  // Get all unique models
  const models = Array.from(new Set(data.map(d => d.model)));

  // Group by metric
  const grouped = data.reduce<Record<string, ChartRow>>((acc, cur) => {
    if (!acc[cur.metric]) acc[cur.metric] = { metric: cur.metric };
    acc[cur.metric][`${cur.model}_low`] = cur.ci_low;
    acc[cur.metric][`${cur.model}_range`] = cur.ci_high - cur.ci_low;
    return acc;
  }, {});
  const chartData: ChartRow[] = Object.values(grouped);

  return (
    <BarChart
      width={730}
      height={300}
      data={chartData}
      margin={{ top: 20, right: 20, bottom: 20, left: 40 }}
    >
      <XAxis dataKey="metric" />
      <YAxis />
      <Tooltip
        formatter={(value, name, props) => {
          const dataKey = props?.dataKey;
          if (typeof dataKey !== 'string') return [value, name];

          const key = dataKey.replace('_range', '');
          const low = props.payload?.[`${key}_low`] ?? 0;
          return [`${low} - ${low + value}`, key];
        }}
      />
      <Legend formatter={(value: string) => value.replace('_range', '')}/>
      {models.map(model => (
        <Bar
          key={model}
          dataKey={`${model}_range`}
          stackId={model}
          fill={getColor(model)}
        />
      ))}
    </BarChart>
  );
}

function getColor(model: string): string {
  const colorMap: Record<string, string> = {
    
  };
  return colorMap[model] || getRandomColor(model);
}

// Optional fallback for unknown models
function getRandomColor(seed: string): string {
  // Create a hash-based color
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = seed.charCodeAt(i) + ((hash << 5) - hash);
  }
  const color = `hsl(${hash % 360}, 70%, 50%)`;
  return color;
}