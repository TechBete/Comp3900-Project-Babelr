import { Box, Typography, List, ListItem } from "@mui/material";


// interface DemographicsData {
//     total_listeners: number;
//     native: number;
//     non_native: number;
//     countries: string[];
//     male: number;
//     female: number;
//   }
  

// export default function DemographicsBox({ demographics }: { demographics: DemographicsData }) {
//   return (
//     <Box sx={{ p: 2, border: '1px solid orange', borderRadius: 1 }}>
//       <Typography variant="h6">Listener Demographics</Typography>
//       <List>
//         <ListItem>{demographics.total_listeners} Listeners</ListItem>
//         <ListItem>Languages: {demographics.native} Native, {demographics.non_native} Non-native</ListItem>
//         <ListItem>Countries: {demographics.countries.join(', ')}</ListItem>
//         <ListItem>Gender: {demographics.male} Male, {demographics.female} Female</ListItem>
//       </List>
//     </Box>
//   );
// }

export default function DemographicsBox() {
  const demographics = {
    total_listeners: 100,
    native: 80,
    non_native: 20,
    countries: ['Australia', 'USA', 'Canada'],
    male: 50,
    female: 50,
  };

  return (
    <Box sx={{ p: 2}}>
      <Typography variant="h6">Listener Demographics</Typography>
      <List>
        <ListItem>{demographics.total_listeners} Listeners</ListItem>
        <ListItem>Languages: {demographics.native} Native, {demographics.non_native} Non-native</ListItem>
        <ListItem>Countries: {demographics.countries.join(', ')}</ListItem>
        <ListItem>Gender: {demographics.male} Male, {demographics.female} Female</ListItem>
      </List>
    </Box>
  );
}