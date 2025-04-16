import * as React from 'react';
import { useRouter } from 'next/router';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Link from 'next/link';

const drawerWidth = 240;

type Props = {
    project_name: string;
};

const routeKeys = ['Audio Clips', 'Metrics', 'Analytics'] as const;
type RouteKey = typeof routeKeys[number];

const routeSuffixes: Record<RouteKey, string> = {
  'Audio Clips': 'audioclips',
  'Metrics': 'metrics',
  'Analytics': 'analytics'
};

export default function Sidebar({ project_name }: Props) {
  const router = useRouter();
  const { userId, projectName } = router.query;


  return (
    <Box sx={{ display: 'flex' }}>
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
            color: '#e7e9de'
          },
        }}
      >
        <Box sx={{ overflow: 'auto' }}>
          <List>
            <ListItem key="ProjectName" sx={{ justifyContent: 'center', textAlign: 'center' }} >
              <ListItemText primary={project_name} slotProps={{ primary: { sx: { fontSize: 20, fontWeight: 'bold' } } }} />
            </ListItem>
          </List>
          <Divider />
          <List>
            {routeKeys.map((key) => {
              const href = userId && projectName
                ? `/app/audioData/${userId}/${projectName}/${routeSuffixes[key]}`
                : '#';

              return (
                <ListItem key={key} disablePadding>
                  <ListItemButton component={Link} href={href}>
                    <ListItemIcon />
                    <ListItemText primary={key} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
          <Divider />
        </Box>
      </Drawer>
    </Box>
  );
}