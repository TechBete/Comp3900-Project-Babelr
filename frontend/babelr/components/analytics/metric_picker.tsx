import { useEffect, useState } from "react";
import { Box, Typography, Select, MenuItem, SelectChangeEvent } from '@mui/material';
import { useRouter } from "next/router";

interface MetricPickerProps {
    onMetricSelect: (metric: string) => void;
}

export default function MetricPicker({ onMetricSelect }: MetricPickerProps) {
    const [availableMetrics, setAvailableMetrics] = useState<string[]>([]);
    const [selectedMetric, setSelectedMetric] = useState<string>('');
    const router = useRouter();
    const { projectName } = router.query;

    useEffect(() => {
        if (typeof projectName === 'string') {
            getMetrics();
        }
    }, [projectName]);

    async function getMetrics() {
        try {
            const res = await fetch('http://localhost:8016/projects/getProjectMetrics', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_name: projectName }),
            });
            const data = await res.json();
            if (data.metrics && typeof data.metrics === 'object') {
                const keys = Object.keys(data.metrics);
                setAvailableMetrics(keys);
                setSelectedMetric(keys[0]); // default select first metric
                onMetricSelect(keys[0]);    // pass default selection to parent
            }
        } catch (e) {
            console.log("Failed to get metrics", e);
        }
    }

    const handleChange = (event: SelectChangeEvent) => {
        const newMetric = event.target.value;
        setSelectedMetric(newMetric);
        onMetricSelect(newMetric);
    };

    if (typeof projectName !== 'string') {
        return <div>Loading?</div>;
    }

    return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h6">Metric Type:</Typography>
            <Select
                value={selectedMetric}
                onChange={handleChange}
                size="small"
            >
                {availableMetrics.map((metric) => (
                    <MenuItem key={metric} value={metric}>
                        {metric}
                    </MenuItem>
                ))}
            </Select>
        </Box>
    );
}