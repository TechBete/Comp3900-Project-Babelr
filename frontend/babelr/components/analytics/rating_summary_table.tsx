import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Box } from '@mui/material'

export type SummaryRowRes = {
  model: string,
  language: string,
  mean: number,
  std: number,
  ci_low: number,
  ci_high: number
}

export type SummaryRow = {
  model: string,
  language: string,
  mean: number,
  std: number,
  ci: string
}

type Props = {
  data: SummaryRowRes[]
}

export default function RatingsSummaryTable({data}: Props) {
  const columns: GridColDef[] = [
    { field: 'model', headerName: 'Model', flex: 1 },
    { field: 'language', headerName: 'Language', flex: 1 },
    { field: 'mean', headerName: 'Mean', flex: 1 },
    { field: 'std', headerName: 'Std Dev', flex: 1 },
    { field: 'ci', headerName: '95% CI', flex: 1 },
  ];

  // const rows = [
  //   { id: 1, model: 'M1', language: 'EN',  mean: 1.0, std: 0.8, ci: '[0.1, 1.9]' },
  //   { id: 2, model: 'M1', language: 'EN',  mean: 1.5, std: 0.7, ci: '[0.6, 2.4]' },
  //   { id: 3, model: 'M1', language: 'CH',  mean: 0.5, std: 0.5, ci: '[0, 1]' },
  //   { id: 4, model: 'M2', language: 'EN',  mean: 1.8, std: 0.4, ci: '[1.2, 2.4]' },
  //   { id: 5, model: 'M2', language: 'CH',  mean: 0.9, std: 0.6, ci: '[0, 1.8]' },
  // ];
  const flattened = (data).map((entry) => {
    const summaryObj: SummaryRow = {
      model: entry.model,
      language: entry.language,
      mean: entry.mean,
      std: entry.std,
      ci: `[${entry.ci_low.toFixed(2)} - ${entry.ci_high.toFixed(2)}]`
    };
    return summaryObj;
  })

  const rows = flattened.map((row, index) => ({
    id: index,
    ...row,
  }));

  return (
    <Box sx={{ width: '100%' , overflowX: 'auto'}}>
        <DataGrid
        rows={rows}
        columns={columns}
        disableRowSelectionOnClick
        density='compact'
        hideFooter
        />
    </Box>
  );
}