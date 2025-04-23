import { Box, Button } from '@mui/material';

export default function ExportButtons() {
  return (
    <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
      <Button 
        variant="outlined"
        sx={{
          color: '#2b4450',
          borderColor: '#2b4450',
          '&:hover': {
            backgroundColor: '#2b4450',
            color: '#ffffff',
            borderColor: '#2b4450',
          }
        }}>
          Export CSV
        </Button>
      <Button 
        variant="outlined"
        sx={{
          color: '#2b4450',
          borderColor: '#2b4450',
          '&:hover': {
            backgroundColor: '#2b4450',
            color: '#ffffff',
            borderColor: '#2b4450',
          }
        }}>
          Export JSON
        </Button>
      <Button 
        variant="outlined"
        sx={{
          color: '#2b4450',
          borderColor: '#2b4450',
          '&:hover': {
            backgroundColor: '#2b4450',
            color: '#ffffff',
            borderColor: '#2b4450',
          }
        }}>
          Export PDF
      </Button>
    </Box>
  );
}