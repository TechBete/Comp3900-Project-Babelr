import Navbar from "components/nav_bar_researcher";
import Sidebar from "components/project_sidebar";
import RatingChart, { SummaryStat } from "components/analytics/rating_chart";
import DemographicsBox from "components/analytics/demographics_box";
import RatingsTable from "components/analytics/rating_table";
import ExportButtons from "components/analytics/export_button";
import RatingsSummaryTable from "components/analytics/rating_summary_table";
import RoleCheck from "components/role_checker";

import { Box, Typography, Divider } from '@mui/material';

export default function AnalyticsPage() {

    const summaryStats: SummaryStat[] = [
        // Naturalness
        { clipId: 'clipA1', metric: 'Naturalness', model: 'A', mean: 4.2, std: 0.5, ci: '3.5 - 4.9' },
        { clipId: 'clipB1', metric: 'Naturalness', model: 'B', mean: 3.7, std: 0.4, ci: '3.0 - 4.4' },
        { clipId: 'clipC1', metric: 'Naturalness', model: 'C', mean: 3.9, std: 0.6, ci: '3.1 - 4.7' },
      
        // Intelligibility
        { clipId: 'clipA2', metric: 'Intelligibility', model: 'A', mean: 4.5, std: 0.3, ci: '4.0 - 5.0' },
        { clipId: 'clipB2', metric: 'Intelligibility', model: 'B', mean: 4.0, std: 0.5, ci: '3.2 - 4.8' },
        { clipId: 'clipC2', metric: 'Intelligibility', model: 'C', mean: 4.1, std: 0.4, ci: '3.5 - 4.7' },
      
        // Clarity
        { clipId: 'clipA3', metric: 'Clarity', model: 'A', mean: 4.3, std: 3, ci: '3.7 - 4.9' },
        { clipId: 'clipB3', metric: 'Clarity', model: 'B', mean: 3.9, std: 0.6, ci: '3.0 - 4.8' },
        { clipId: 'clipC3', metric: 'Clarity', model: 'C', mean: 4.0, std: 0.5, ci: '3.2 - 4.8' },
      
        // New Metric
        { clipId: 'clipA4', metric: 'new metrics', model: 'A', mean: 3.3, std: 3.4, ci: '3.7 - 4.9' },
        { clipId: 'clipB4', metric: 'new metrics', model: 'B', mean: 3.9, std: 3.6, ci: '3.0 - 4.8' },
        { clipId: 'clipC4', metric: 'new metrics', model: 'C', mean: 3.0, std: 2.5, ci: '3.2 - 4.8' },
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
            width: '100%'
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