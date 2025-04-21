import { useState } from 'react';
import {
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  OutlinedInput,
  Checkbox,
  ListItemText,
  Typography,
} from '@mui/material';
import { BarChart } from '@mui/x-charts/BarChart';
import ConfidenceIntervalChart from './confidence_interval_chart';

export type ChartType = 'mean' | 'std' | 'ci';

export type GraphStat = {
  metric: string;
  model: string;
  mean: number;
  std: number;
  ci_low: number;
  ci_high: number;
};

type Props = {
  data:GraphStat[];
};

export default function RatingChart({ data }: Props) {
  const allModels = Array.from(new Set(data.map((d) => d.model)));
  const allMetrics = Array.from(new Set(data.map((d) => d.metric)));

  const [selectedModels, setSelectedModels] = useState<string[]>(allModels);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(allMetrics);
  const [chartType, setChartType] = useState<ChartType>('mean');

  const filtered = data.filter(
    (d) => selectedModels.includes(d.model) && selectedMetrics.includes(d.metric)
  );
  console.log(filtered);

  const getMeanDataset = () => {
    return selectedMetrics.map((metric) => {
      const row: { metric: string; [model: string]: number | string } = { metric };
      selectedModels.forEach((model) => {
        const entry = filtered.find((d) => d.metric === metric && d.model === model);
        row[model] = entry?.mean ?? 0;
      });
      return row;
    });
  };

  const getSTDDataset = () => {
    return selectedModels.map((model) => ({
      label: model,
      data: filtered
        .filter((d) => d.model === model)
        .map((d) => ({
          x: d.metric,
          y: d.std,
        })),
    }));
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* Controls */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
        <FormControl sx={{ minWidth: 160 }} size="small">
          <InputLabel>Chart Type</InputLabel>
          <Select
            value={chartType}
            onChange={(e) => setChartType(e.target.value as ChartType)}
            input={<OutlinedInput label="Chart Type" />}
          >
            <MenuItem value="mean">Mean</MenuItem>
            <MenuItem value="std">Standard Deviation</MenuItem>
            <MenuItem value="ci">95% Confidence Interval</MenuItem>
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 200 }} size="small">
          <InputLabel>Models</InputLabel>
          <Select
            multiple
            value={selectedModels}
            onChange={(e) =>
              setSelectedModels(
                typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value
              )
            }
            input={<OutlinedInput label="Models" />}
            renderValue={(selected) => selected.join(', ')}
          >
            {allModels.map((model) => (
              <MenuItem key={model} value={model}>
                <Checkbox checked={selectedModels.includes(model)} />
                <ListItemText primary={model} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 200 }} size="small">
          <InputLabel>Metrics</InputLabel>
          <Select
            multiple
            value={selectedMetrics}
            onChange={(e) =>
              setSelectedMetrics(
                typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value
              )
            }
            input={<OutlinedInput label="Metrics" />}
            renderValue={(selected) => selected.join(', ')}
          >
            {allMetrics.map((metric) => (
              <MenuItem key={metric} value={metric}>
                <Checkbox checked={selectedMetrics.includes(metric)} />
                <ListItemText primary={metric} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Chart */}
      <Box sx={{ width: '100%', overflowX: 'auto' }}>
  			{selectedModels.length === 0 || selectedMetrics.length === 0 ? (
    	<Typography sx={{ p: 2 }}>
     	 Please select at least one model and one metric to display the chart.
    	</Typography>
  ) : chartType === 'mean' ? (
    <BarChart
      dataset={getMeanDataset()}
      xAxis={[{ scaleType: 'band', dataKey: 'metric' }]}
      series={selectedModels.map((model) => ({
        dataKey: model,
        label: model,
      }))}
      grid={{ horizontal: true }}
      borderRadius={20}
      height={300}
    />
  ) : chartType === 'std' ? (
    <BarChart
      dataset={selectedMetrics.map((metric) => {
        const row: { metric: string; [model: string]: number | string } = { metric };
        selectedModels.forEach((model) => {
          const entry = filtered.find((d) => d.metric === metric && d.model === model);
          row[model] = entry?.std ?? 0;
        });
        return row;
      })}
      xAxis={[{ scaleType: 'band', dataKey: 'metric' }]}
      series={selectedModels.map((model) => ({
        dataKey: model,
        label: model,
      }))}
      grid={{ horizontal: true }}
      borderRadius={20}
      height={300}
    />
  ): (
    <ConfidenceIntervalChart data={filtered}/>
  )}
      </Box>
    </Box>
  );
}