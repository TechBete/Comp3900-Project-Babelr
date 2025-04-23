import Navbar from "components/nav_bar_researcher";
import Sidebar from "components/project_sidebar";
import RatingChart, {  GraphStat } from "components/analytics/rating_chart";
import DemographicsBox from "components/analytics/demographics_box";
import RatingsTable, { RatingsRow, RawRatingsRow } from "components/analytics/rating_table";
import ExportButtons from "components/analytics/export_button";
import RatingsSummaryTable, { SummaryRowRes } from "components/analytics/rating_summary_table";
import RoleCheck from "components/role_checker";

import { Box, Typography, Divider} from '@mui/material';
import { useEffect, useState } from "react";
import Metrics from "components/analytics/metric_picker";
import { useRouter } from "next/router";

async function getRatingStats(projectName: string, metric: string): Promise<RatingsRow[] | null>{
  try {
    const response = await fetch('http://localhost:8016/statistics/getRatingsStats' , {
        method:"POST",
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({project_name: projectName, metric: metric}),
    })
    
    if (response.ok) {
        const res = await response.json();
        console.log('stats:', res['rating_stats']);
        const flattened = (res.rating_stats as RawRatingsRow[]).map((entry) => {
          const ratingObj: RatingsRow = {
            audio: entry.audio,
            model: entry.model,
            language: entry.language,
          };
        
          entry.ratings.forEach((val, idx) => {
            ratingObj[`r${idx + 1}`] = val;
          });
        
          return ratingObj;
        });
  
        return flattened;
    } else {
        const error = await response.json()
        console.log(error)
        return null;
    }
  } catch(e) {
    console.error('Fetch error:', e);
    return null;
  }
}

async function getSummaryStats(projectName: string): Promise<SummaryRowRes[] | null> {
  try {
    const response = await fetch('http://localhost:8016/statistics/getProjectSummary' , {
        method:"POST",
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({project_name: projectName}),
    })
    
    if (response.ok) {
        const res = await response.json();
        console.log('stats:', res['summary_stats']);
        return res.summary_stats as SummaryRowRes[];
    } else {
        const error = await response.json()
        console.log(error)
        return null;
    }
  } catch(e) {
    console.error('Fetch error:', e);
    return null;
  }
}

async function getGraphStats(projectName: string): Promise<GraphStat[] | null> {
  try {
    const response = await fetch('http://localhost:8016/statistics/getGraphStats' , {
        method:"POST",
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({project_name: projectName}),
    })
    
    if (response.ok) {
        const res = await response.json();
        console.log('stats:', res['graph_stats']);
        return res.graph_stats as GraphStat[];
    } else {
        const error = await response.json()
        console.log(error)
        return null;
    }
  } catch(e) {
    console.error('Fetch error:', e);
    return null;
  }  
}


export default function AnalyticsPage() {
  const [metric, setMetric] = useState<string>('');
  const [rawAudioData, setRawAudioData] = useState<RatingsRow[] | null>(null);
  const [summaryData, setSummaryData] = useState<SummaryRowRes[] | null>(null);
  const [graphData, setGraphData] =useState<GraphStat[] | null>(null);
  const router = useRouter();
  const { projectName } = router.query; //  project name

  useEffect(() => {
    if (typeof projectName !== 'string') return;
    const confirmedName: string = projectName; 
  
    async function fetchStats() {
      const data = await getRatingStats(confirmedName, metric);
      const summary = await getSummaryStats(confirmedName);
      const graph = await getGraphStats(confirmedName);
      setRawAudioData(data);
      setSummaryData(summary);
      setGraphData(graph);
    }
  
    fetchStats();
  }, [metric, projectName]);

  if (typeof projectName !== 'string') {
    return <div>Loading?</div>;
  }
  

    // const summaryStats: SummaryStat[] = [
    //     // Naturalness
    //     { clipId: 'clipA1', metric: 'Naturalness', model: 'A', mean: 4.2, std: 0.5, ci_low: 3.5, ci_high: 4.9 },
    //     { clipId: 'clipB1', metric: 'Naturalness', model: 'B', mean: 3.7, std: 0.4, ci_low: 3.5, ci_high: 4.9 },
    //     { clipId: 'clipC1', metric: 'Naturalness', model: 'C', mean: 3.9, std: 0.6, ci_low: 3.5, ci_high: 4.9 },
      
    //     // Intelligibility
    //     { clipId: 'clipA2', metric: 'Intelligibility', model: 'A', mean: 4.5, std: 0.3, ci_low: 3.5, ci_high: 4.9 },
    //     { clipId: 'clipB2', metric: 'Intelligibility', model: 'B', mean: 4.0, std: 0.5, ci_low: 3.5, ci_high: 4.9 },
    //     { clipId: 'clipC2', metric: 'Intelligibility', model: 'C', mean: 4.1, std: 0.4, ci_low: 3.5, ci_high: 4.9 },
      
    //     // Clarity
    //     { clipId: 'clipA3', metric: 'Clarity', model: 'A', mean: 4.3, std: 3, ci_low: 3.5, ci_high: 4.9 },
    //     { clipId: 'clipB3', metric: 'Clarity', model: 'B', mean: 3.9, std: 0.6, ci_low: 3.5, ci_high: 4.9 },
    //     { clipId: 'clipC3', metric: 'Clarity', model: 'C', mean: 4.0, std: 0.5, ci_low: 3.5, ci_high: 4.9 },
      
    //     // New Metric
    //     { clipId: 'clipA4', metric: 'new metrics', model: 'A', mean: 3.3, std: 3.4, ci_low: 3.5, ci_high: 4.9 },
    //     { clipId: 'clipB4', metric: 'new metrics', model: 'B', mean: 3.9, std: 3.6, ci_low: 3.5, ci_high: 4.9 },
    //     { clipId: 'clipC4', metric: 'new metrics', model: 'C', mean: 3.0, std: 2.5, ci_low: 3.5, ci_high: 4.9 },
    //   ];

  return (
    <RoleCheck requiredRole="researcher">
      <Navbar />
      <Box sx={{ display: "flex", backgroundColor: "#DFEBED", minHeight: "100vh"}}>
        <Sidebar project_name={projectName} />

        <Box sx={{ flexGrow: 1, overflowX:'hidden', display: "flex", flexDirection: "column", mt: "50px", p: 3, gap: 4 }}>

          <Typography variant="h4" gutterBottom>Analytics Dashboard</Typography>
          {/* Top Section */}
          <Box sx={{ display: "flex", gap: 2 }}>
            <Box sx={{
              flexGrow:1,
              border: '2px solid #f57c00',
              borderRadius: 2,
              p: 2,
              backgroundColor: '#fff3e0',
              boxShadow: 2,
              }}>
              <Typography variant="h6" sx={{ mb: 1 }}>Summary Statistics</Typography>
              <Divider sx={{ mb: 2 }} />
              {summaryData? <RatingsSummaryTable data={summaryData}/>: <div>No Data</div>}
            </Box>
            
            {/* <Box sx={{
              flexGrow: 1,
              border: '2px solid #1976d2',
              borderRadius: 2,
              p: 2,
              backgroundColor: '#e3f2fd',
              boxShadow: 2,
            }}>
              {summaryData? <RatingChart data={summaryStats}/>: <div>No Data</div> }
            </Box> */}

            <Box sx={{
              width: 300,
              border: '2px solid #1976d2',
              borderRadius: 2,
              p: 2,
              backgroundColor: '#e3f2fd',
              boxShadow: 2,
            }}>
              <DemographicsBox projectName={projectName} />
            </Box>
          </Box>

          {/* Middle Section - Summary Stats */}
          <Box sx={{ flexGrow: 1, border: '2px solid #1976d2', borderRadius: 2, p: 2, backgroundColor: '#e3f2fd', boxShadow: 2 }}>
            {graphData ? <RatingChart data={graphData} /> : <div>No data</div>}
          </Box>

          <Metrics onMetricSelect={(metric: string) => setMetric(metric)}/>
          {/* <Typography variant="h4" gutterBottom>Metric is {metric}</Typography> */}

          {/* Bottom Section - Raw Data */}
          <Box sx={{
            border: '2px solid #388e3c',
            borderRadius: 2,
            p: 2,
            backgroundColor: '#e8f5e9',
            boxShadow: 2,
            maxWidth: '100%',
            overflowX: 'auto'
          }}>
            <Typography variant="h6" sx={{ mb: 1 }}>{metric} Data</Typography>
            <Divider sx={{ mb: 2 }} />
            {rawAudioData ? <RatingsTable data={rawAudioData} /> : <div>No Data</div>}
          </Box>

          {/* Bottom Section - Summary Stats */}
          {/* <Box sx={{
            border: '2px solid #f57c00',
            borderRadius: 2,
            p: 2,
            backgroundColor: '#fff3e0',
            boxShadow: 2,
          }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Summary Statistics</Typography>
            <Divider sx={{ mb: 2 }} />
            <RatingsSummaryTable />
          </Box> */}

          {/* Export Buttons */}
          <Box sx={{ mt: 2 }}>
            <ExportButtons />
          </Box>

        </Box>
      </Box>
    </RoleCheck>
  );
}