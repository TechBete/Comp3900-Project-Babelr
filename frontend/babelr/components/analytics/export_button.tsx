import { Box, Button } from '@mui/material';

export default function ExportButtons() {
  return (
    <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
      <Button variant="outlined">Export CSV</Button>
      <Button variant="outlined">Export JSON</Button>
      <Button variant="outlined">Export PDF</Button>
    </Box>
  );
}