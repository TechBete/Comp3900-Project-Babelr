import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Box } from '@mui/material'


export type RatingsRow = {
  audio: string;
  model: string;
  language: string;
  [key: string]: string | number; // allows dynamic r1–rN keys
};

export type RawRatingsRow = {
  audio: string;
  model: string;
  language: string;
  ratings: number[];
};

type Props = {
  data: RatingsRow[];
};

export default function RatingsTable({ data }: Props) {
  if (data.length === 0) return null;
  const ratingKeys = Object.keys(data[0]).filter(
    (key) => /^r\d+$/i.test(key)
  );

  // const rows = [
  //   { id: 1, audio: 'A1', model: 'M1', language: 'EN', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 2, audio: 'A2', model: 'M1', language: 'EN', r1: 2, r2: 2, r3: 1.3, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 3, audio: 'A3', model: 'M1', language: 'CH', r1: 1, r2: 1, r3: 0.7, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 4, audio: 'A4', model: 'M2', language: 'EN', r1: 2, r2: 2, r3: 1.1, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  //   { id: 5, audio: 'A5', model: 'M2', language: 'CH', r1: 0, r2: 1, r3: 0.5, r4: 1, r5: 1, r7: 1, r8: 1, r9: 1 },
  // ];

  const columns: GridColDef[] = [
    { field: 'audio', headerName: 'Audio', minWidth: 150, flex: 0,   },
    { field: 'model', headerName: 'Model', minWidth: 100, flex: 0,   },
    { field: 'language', headerName: 'Language', minWidth: 100, flex: 0,   },
    ...ratingKeys.map((key) => ({
      field: key,
      headerName: key.toUpperCase(),
      width: 100,
    })),
  ];

  const rows = data.map((row, index) => ({
    id: index,
    ...row,
  }));

  return (
        <Box sx={{ width: '100%', overflow: 'auto' }}>
            <Box sx={{ height: 400, maxWidth: '100%' }}>
            {/* <Box sx={{ minWidth: 1200, height: 400 }}> */}
                <DataGrid
                    // disableColumnResize
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