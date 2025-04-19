import { BarChart } from '@mui/x-charts/BarChart';
import { LineChart } from '@mui/x-charts/LineChart';
import { useState } from 'react';
import { Box, Select, MenuItem, Typography } from '@mui/material';


// export type RatingData = Record<string, number>;

// export default function RatingChart({ dataset }: { dataset: RatingData[] }) {

//   return (
//     <BarChart
//       dataset={dataset}
//       xAxis={[{ scaleType: 'band', dataKey: 'name' }]}
//       series={[
//         { dataKey: 'ModelA', label: 'Model A' },
//         { dataKey: 'ModelB', label: 'Model B' },
//         { dataKey: 'ModelC', label: 'Model C' },
//       ]}
//       grid={{ horizontal: true }}
//       borderRadius={20}
//     />
//   );
// }
export type ChartType = 'mean' | 'std' | 'ci';

export type SummaryStat = {
    metric: string;
    modelA: number;
    modelB: number;
    modelC: number;
    stdA: number;
    stdB: number;
    stdC: number;
    ciA: string;
    ciB: string;
    ciC: string;
  }
  


export default function RatingChart({ data }: { data: SummaryStat[] }) {
    const [chartType, setChartType] = useState<'mean' | 'std' | 'ci'>('mean');
    const isLineChart = chartType === 'std';
    
    const series = {
        mean: [
          { dataKey: 'modelA', label: 'Model A' },
          { dataKey: 'modelB', label: 'Model B' },
          { dataKey: 'modelC', label: 'Model C' },
        ],
        std: [
          { dataKey: 'stdA', label: 'Model A Std' },
          { dataKey: 'stdB', label: 'Model B Std' },
          { dataKey: 'stdC', label: 'Model C Std' },
        ],
        ci: [
          { dataKey: 'ciA', label: 'Model A CI' },
          { dataKey: 'ciB', label: 'Model B CI' },
          { dataKey: 'ciC', label: 'Model C CI' },
        ],
      }[chartType];

      console.log(data)
      console.log(series)
  
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
            <Box sx={{width: '100%', overflowX: 'auto'}}>
                {isLineChart ? (
                    <LineChart
                        dataset={data as Record<string, number | string>[]}
                        xAxis={[{ scaleType: 'band', dataKey: 'metric' }]}
                        series={series.map(s => ({ ...s, curve: 'monotoneX' }))}
                        height={300}
                    />
                ) : (
                    <BarChart
                        dataset={data as Record<string, number | string>[]}
                        xAxis={[{ scaleType: 'band', dataKey: 'metric' }]}
                        series={series}
                        grid={{ horizontal: true }}
                        borderRadius={20}
                        height={300}
                    />
                )}
            </Box>
        </Box>
      );
}