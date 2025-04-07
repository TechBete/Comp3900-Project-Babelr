import * as React from 'react';
import Box from '@mui/material/Box';
import Fab from '@mui/material/Fab';
import AddIcon from '@mui/icons-material/Add';
import styles from 'stylesheets/projects_list.module.css'

export default function CreateButton({ onClick }: { onClick: () => void }) {
  return (
    <Box sx={{ '& > :not(style)': { m: 1 } }}>
      <Fab className={styles['add-project-btn']}color="secondary" aria-label="add" onClick={onClick}>
        <AddIcon />
      </Fab>
    </Box>
  );
}