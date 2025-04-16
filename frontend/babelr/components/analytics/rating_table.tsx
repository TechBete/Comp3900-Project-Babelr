import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Box } from '@mui/material'

export default function RatingsTable() {
  const metrics = ['r1', 'r2', 'r3', 'r4', 'r5', 'r7', 'r8', 'r9'];

  const rows = [
    { id: 1, audio: 'A1', model: 'M1', language: 'EN', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 2, audio: 'A2', model: 'M1', language: 'EN', r1: 2, r2: 2, r3: 1.3, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 3, audio: 'A3', model: 'M1', language: 'CH', r1: 1, r2: 1, r3: 0.7, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 4, audio: 'A4', model: 'M2', language: 'EN', r1: 2, r2: 2, r3: 1.1, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
    { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  ];

  const columns: GridColDef[] = [
    { field: 'audio', headerName: 'Audio', flex: 1 },
    { field: 'model', headerName: 'Model', flex: 1 },
    { field: 'language', headerName: 'Language', flex: 1 },
    ...metrics.map((metric) => ({
      field: metric,
      headerName: metric.toUpperCase(),
      flex: 1
    })),
  ];

  return (
        <Box sx={{ width: '100%', overflow: 'auto' }}>
            <Box sx={{ height: 400, maxWidth: '100%' }}>
                <DataGrid
                    rows={rows}
                    columns={columns}
                    hideFooter
                    disableRowSelectionOnClick
                    density="compact"
                />
            </Box>
        </Box>
  );
}

// interface RatingTableRow {
//     id: number;
//     clip: string;
//     metric: string;
//     mean: number;
//     std: number;
//     count: number;
//   }

// export default function RatingsTable({ rows }: { rows: RatingTableRow[] }) {
//   return <DataGrid rows={rows} columns={columns} autoHeight disableRowSelectionOnClick />;
// }