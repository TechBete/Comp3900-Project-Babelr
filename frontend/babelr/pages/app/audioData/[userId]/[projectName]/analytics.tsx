import Navbar from "components/nav_bar_researcher";
import Sidebar from "components/project_sidebar";
import RatingChart, {  GraphStat } from "components/analytics/rating_chart";
import DemographicsBox from "components/analytics/demographics_box";
import RatingsTable, { RatingsRow, RawRatingsRow } from "components/analytics/rating_table";
import ExportButtons from "components/analytics/export_button";
import RatingsSummaryTable, { SummaryRowRes } from "components/analytics/rating_summary_table";
import RoleCheck from "components/role_checker";
import Metrics from "components/analytics/metric_picker";

import { styles } from "stylesheets/analytics.module";
import { Box, Typography, Divider} from '@mui/material';
import { useEffect, useState } from "react";
import { useRouter } from "next/router";

// fetching rating stats from the backend
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
// fetching summary stats from the backend
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
// fetching graph stats from the backend
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

    // fetches data whenever metric/project name is changed
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

  // placeholder if issues with getting projectName
  if (typeof projectName !== 'string') {
    return <div>Loading?</div>;
  }
  
  return (
    <RoleCheck requiredRole="researcher">
      <Navbar />
      <Box sx={styles.pageContainer}>
        <Sidebar project_name={projectName} />

        <Box sx={styles.contentContainer}>
          <Typography variant="h4" sx={styles.heading}>
            Analytics Dashboard
          </Typography>
          {/* Top Section - Summary and demogrpahics */}
          <Box sx={{ display: "flex", gap: 2 }}>
            {/* Summary Box */}
            <Box sx={styles.summaryBox}>
              <Typography variant="h6" sx={styles.subHeading}>
                Summary Statistics
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {summaryData? <RatingsSummaryTable data={summaryData}/>: <div>No Data</div>}
            </Box>
            {/* Demographics Box*/}
            <Box sx={styles.demographicsBox}>
              <DemographicsBox projectName={projectName} />
            </Box>
          </Box>

          {/* Middle Section - Summary Stats (displaying as a graph) */}
          <Box sx={styles.graphBox}>
            {graphData ? <RatingChart data={graphData} /> : <div>No data</div>}
          </Box>
          <Metrics onMetricSelect={(metric: string) => setMetric(metric)}/>

          {/* Bottom Section - Raw Data Output */}
          <Box sx={styles.tableBox}>
            <Typography variant="h6" sx={{ mb: 1 }}>{metric} Data</Typography>
            <Divider sx={{ mb: 2 }} />
            {rawAudioData ? <RatingsTable data={rawAudioData} /> : <div>No Data</div>}
          </Box>

          {/* Export Buttons */}
          <Box sx={styles.exportBox}>
            <ExportButtons />
          </Box>
        </Box>
      </Box>
    </RoleCheck>
  );
}