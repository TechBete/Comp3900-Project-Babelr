import { BarChart } from '@mui/x-charts/BarChart';
import { LineChart } from '@mui/x-charts/LineChart';
import { useState } from 'react';
import { Box, Select, MenuItem, Typography } from '@mui/material';

export type ChartType = 'mean' | 'std' | 'ci';

export type SummaryStat = {
  clipId: string;
  model: string;
  metric: string;
  mean: number;
  std: number;
  ci: string; // e.g., "4.2 - 4.7"
};

type Props = {
  data: SummaryStat[];
};

type AggregatedRow = {
  metric: string;
  [key: string]: string | number;
};

export default function RatingChart({ data }: Props) {
  const [chartType, setChartType] = useState<ChartType>('mean');

  const parseCI = (ci: string): [number, number] => {
    const [lower, upper] = ci.split('-').map(s => parseFloat(s.trim()));
    return [lower, upper];
  };

  const aggregateByMetric = () => {
    const metrics = Array.from(new Set(data.map(d => d.metric)));
    const models = Array.from(new Set(data.map(d => d.model)));

    return metrics.map(metric => {
      const clips = data.filter(d => d.metric === metric);
      const row: AggregatedRow = { metric };

      models.forEach(model => {
        const modelClips = clips.filter(c => c.model === model);
        const means = modelClips.map(c => c.mean);
        const avg = means.reduce((a, b) => a + b, 0) / means.length || 0;

        row[model] = avg;

        const [avgLow, avgHigh] = (() => {
          const bounds = modelClips.map(c => parseCI(c.ci));
          const lows = bounds.map(([low]) => low);
          const highs = bounds.map(([, high]) => high);
          const lowAvg = lows.reduce((a, b) => a + b, 0) / lows.length || 0;
          const highAvg = highs.reduce((a, b) => a + b, 0) / highs.length || 0;
          return [lowAvg, highAvg];
        })();

        row[`ciLow_${model}`] = avg - avgLow;
        row[`ciHigh_${model}`] = avgHigh - avg;
      });

      return row;
    });
  };

  const ciData = aggregateByMetric();
  const models = Array.from(new Set(data.map(d => d.model)));

  const ciSeries = models.map(model => ({
    dataKey: model,
    label: `Model ${model}`,
    errorBars: {
      type: 'vertical',
      lower: ciData.map(d => d[`ciLow_${model}`]),
      upper: ciData.map(d => d[`ciHigh_${model}`]),
    },
  }));

  const meanSeries = models.map(model => ({
    dataKey: model,
    label: `Model ${model}`,
  }));

  const stdDataset = models.map(model => ({
    label: `Model ${model}`,
    data: data
      .filter(d => d.model === model)
      .map(d => ({ x: d.metric, y: d.std })),
  }));

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="h6">Chart Type:</Typography>
        <Select
          value={chartType}
          onChange={(e) => setChartType(e.target.value as ChartType)}
          size="small"
        >
          <MenuItem value="mean">Mean</MenuItem>
          <MenuItem value="std">Standard Deviation</MenuItem>
          <MenuItem value="ci">Confidence Interval</MenuItem>
        </Select>
      </Box>

      <Box sx={{ width: '100%', overflowX: 'auto' }}>
        {chartType === 'std' ? (
          <LineChart
            xAxis={[{ data: stdDataset[0].data.map(d => d.x), scaleType: 'band' }]}
            series={stdDataset.map(series => ({
              data: series.data.map(d => d.y),
              label: series.label,
              curve: 'monotoneX',
            }))}
            height={300}
          />
        ) : (
          <BarChart
            dataset={ciData}
            xAxis={[{ scaleType: 'band', dataKey: 'metric' }]}
            series={chartType === 'mean' ? meanSeries : ciSeries}
            grid={{ horizontal: true }}
            borderRadius={20}
            height={300}
          />
        )}
      </Box>
    </Box>
  );
}