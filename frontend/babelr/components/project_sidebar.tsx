import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';

const drawerWidth = 240;

type Props = {
    project_name: string;
};

export default function Sidebar({project_name}: Props) {
  return (
    <Box sx={{ display: 'flex'}}>
        <Drawer
            variant="permanent"
            sx={{
                width: drawerWidth,
                flexShrink: 0,
                [`& .MuiDrawer-paper`]: { 
                    width: drawerWidth, 
                    boxSizing: 'border-box',
                    position: 'fixed',
                    top: '50px',
                    backgroundColor: '#282D3F',
                    // backgroundColor: '#1e1e1e',
                    color: '#e7e9de'
                },
            }}>
        <Box sx={{ overflow: 'auto' }}>
            <List>
                <ListItem key="ProjectName" sx={{ justifyContent: 'center', textAlign: 'center' }} >
                    <ListItemText primary={project_name} slotProps={{ primary: {sx: {fontSize: 20, fontWeight: 'bold'} }}} />
                </ListItem>
            </List>
            <Divider />
            <List>
                {['Audio Clips', 'Metrics', 'Analytics'].map((text) => (
                <ListItem key={text} disablePadding>
                    <ListItemButton>
                        <ListItemIcon/>
                        <ListItemText primary={text} />
                    </ListItemButton>
                </ListItem>
                ))}
            </List>
            <Divider />
            </Box>
        </Drawer>
      
    </Box>
  );
}