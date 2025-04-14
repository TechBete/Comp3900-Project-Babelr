import Navbar from "components/nav_bar_researcher";
import Sidebar from "components/project_sidebar";
import RatingChart from "components/analytics/rating_chart";
import DemographicsBox from "components/analytics/demographics_box";
import RatingsTable from "components/analytics/rating_table";
import ExportButtons from "components/analytics/export_button";
import RatingsSummaryTable from "components/analytics/rating_summary_table";
import RoleCheck from "components/role_checker";

import { Box, Typography, Divider } from '@mui/material';

export default function AnalyticsPage() {

    const summaryStats = [
        { metric: 'Naturalness', modelA: 4.2, modelB: 3.7, modelC: 3.9, stdA: 0.5, stdB: 0.4, stdC: 0.6, ciA: '[3.5, 4.9]', ciB: '[3.0, 4.4]', ciC: '[3.1, 4.7]' },
        { metric: 'Intelligibility', modelA: 4.5, modelB: 4.0, modelC: 4.1, stdA: 0.3, stdB: 0.5, stdC: 0.4, ciA: '[4.0, 5.0]', ciB: '[3.2, 4.8]', ciC: '[3.5, 4.7]' },
        { metric: 'Clarity', modelA: 4.3, modelB: 3.9, modelC: 4.0, stdA: 0.4, stdB: 0.6, stdC: 0.5, ciA: '[3.7, 4.9]', ciB: '[3.0, 4.8]', ciC: '[3.2, 4.8]' },
        { metric: 'new metrics', modelA: 3.3, modelB: 3.9, modelC: 3.0, stdA: 3.4, stdB: 3.6, stdC: 2.5, ciA: '[3.7, 4.9]', ciB: '[3.0, 4.8]', ciC: '[3.2, 4.8]' },
      ];



  return (
    <RoleCheck requiredRole="researcher">
      <Navbar />
      <Box sx={{ display: "flex" }}>
        <Sidebar project_name="Project 1" />

        <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column", mt: "50px", p: 3, gap: 4 }}>

          <Typography variant="h4" gutterBottom>Analytics Dashboard</Typography>

          {/* Top Section */}
          <Box sx={{ display: "flex", gap: 2 }}>
            <Box sx={{
              flexGrow: 1,
              border: '2px solid #1976d2',
              borderRadius: 2,
              p: 2,
              backgroundColor: '#e3f2fd',
              boxShadow: 2,
            }}>
              <RatingChart data={summaryStats}/>
            </Box>

            <Box sx={{
              width: 300,
              border: '2px solid #1976d2',
              borderRadius: 2,
              p: 2,
              backgroundColor: '#e3f2fd',
              boxShadow: 2,
            }}>
              <DemographicsBox />
            </Box>
          </Box>

          {/* Middle Section - Raw Data */}
          <Box sx={{
            border: '2px solid #388e3c',
            borderRadius: 2,
            p: 2,
            backgroundColor: '#e8f5e9',
            boxShadow: 2,
          }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Raw Ratings Data</Typography>
            <Divider sx={{ mb: 2 }} />
            <RatingsTable />
          </Box>

          {/* Bottom Section - Summary Stats */}
          <Box sx={{
            border: '2px solid #f57c00',
            borderRadius: 2,
            p: 2,
            backgroundColor: '#fff3e0',
            boxShadow: 2,
          }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Summary Statistics</Typography>
            <Divider sx={{ mb: 2 }} />
            <RatingsSummaryTable />
          </Box>

          {/* Export Buttons */}
          <Box sx={{ mt: 2 }}>
            <ExportButtons />
          </Box>

        </Box>
      </Box>
    </RoleCheck>
  );
}