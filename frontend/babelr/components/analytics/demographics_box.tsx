import { useEffect, useState } from "react";
import { Box, Typography, CircularProgress } from "@mui/material";

interface DemographicStats {
  listeners: number;
  languages: Record<string, number>;
  countries: Record<string, number>;
  genders: Record<string, number>;
}

export default function DemographicsBox({ projectName }: { projectName: string }) {
  const [stats, setStats] = useState<DemographicStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("http://localhost:8016/projects/getDemographicStats", {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ project_name: projectName }),
        });

        if (res.ok) {
          const data = await res.json();
          setStats(data);
        } else {
          console.error("Failed to fetch demographic stats");
        }
      } catch (err) {
        console.error("Error fetching demographics:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [projectName]);

  if (loading) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6">Listener Demographics</Typography>
        <CircularProgress size={24} />
      </Box>
    );
  }

  if (!stats) return null;

  return (
    <Box sx={{ p: 2}}>
      <Typography variant="h6" gutterBottom>Listener Demographics</Typography>

      <Typography sx={{ fontWeight: 'bold', mt: 2 }}>Total Listeners</Typography>
      <Typography variant="body1">{stats.listeners}</Typography>

      <Typography sx={{ fontWeight: 'bold', mt: 2 }}>Languages</Typography>
      <Typography variant="body1">
        {Object.entries(stats.languages)
          .map(([lang, count]) => `${lang} (${count})`)
          .join(", ")}
      </Typography>

      <Typography sx={{ fontWeight: 'bold', mt: 2 }}>Countries</Typography>
      <Typography variant="body1">
        {Object.entries(stats.countries)
          .map(([country, count]) => `${country} (${count})`)
          .join(", ")}
      </Typography>

      <Typography sx={{ fontWeight: 'bold', mt: 2 }}>Genders</Typography>
      <Typography variant="body1">
        {Object.entries(stats.genders)
          .map(([gender, count]) => `${gender} (${count})`)
          .join(", ")}
      </Typography>
    </Box>
  );
}