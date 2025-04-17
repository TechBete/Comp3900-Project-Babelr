import React, { useState, ChangeEvent, useEffect } from "react";
import { useRouter } from "next/router";
import {
  Button, Dialog, DialogTitle, DialogContent,
  TextField, Slider, Box, Typography
} from "@mui/material";
import Navbar from "components/nav_bar_researcher";
import Sidebar from "components/project_sidebar";
import RoleCheck from "components/role_checker";

interface Metric {
  name: string;
  minValue: number;
  maxValue: number;
  minLabel: string;
  maxLabel: string;
  description: string;
  value: number;
}

type RawMetric = {
  min: number;
  max: number;
  "minimum label": string;
  "maximum label": string;
  description: string;
};

const MetricsPage = () => {
  const router = useRouter();
  const { projectName } = router.query;

  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [form, setForm] = useState<Metric>({
    name: "",
    minValue: 1,
    maxValue: 5,
    minLabel: "",
    maxLabel: "",
    description: "",
    value: 3,
  });

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: name.includes("Value") ? Number(value) : value });
  };

  // Move fetchMetrics function out of useEffect
  const fetchMetrics = async () => {
    if (!projectName || typeof projectName !== "string") return;

    const response = await fetch(`http://localhost:8016/projects/getProjectMetrics`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ project_name: projectName }),
    });

    const data = await response.json();
    console.log("Fetched metrics response:", data);

    if (data.metrics) {
      const parsedMetrics: Metric[] = (Object.entries(data.metrics) as [string, RawMetric][]).map(
        ([key, metric]) => ({
          name: key,
          minValue: metric.min,
          maxValue: metric.max,
          minLabel: metric["minimum label"],
          maxLabel: metric["maximum label"],
          description: metric.description,
          value: Math.round((metric.min + metric.max) / 2),
        })
      );
      console.log("Parsed metrics array:", parsedMetrics);
      setMetrics(parsedMetrics);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [projectName]);

  const handleSave = async () => {
    if (!projectName || typeof projectName !== "string") return;

    const existingNames = metrics.map((m) => m.name.toLowerCase());
    if (editingIndex === null && existingNames.includes(form.name.toLowerCase())) {
      alert("A metric with this name already exists.");
      return;
    }

    const url = editingIndex !== null
      ? `http://localhost:8016/projects/updateProjectMetrics`
      : `http://localhost:8016/projects/setProjectMetricField`;

    const response = await fetch(url, {
      method: "POST",
      credentials: 'include',
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        project_name: projectName,
        metrics: {
          [form.name]: {
            min: form.minValue,
            max: form.maxValue,
            "minimum label": form.minLabel,
            "maximum label": form.maxLabel,
            description: form.description,
          },
        },
      }),
    });

    const data = await response.json();
    if (data.metrics) {
      fetchMetrics(); // re-fetch after save
    }
    setModalOpen(false);
    setEditingIndex(null);
    resetForm();
  };

  const handleEdit = (index: number) => {
    setForm(metrics[index]);
    setEditingIndex(index);
    setModalOpen(true);
  };

  const handleDelete = async (index: number) => {
    if (!projectName || typeof projectName !== "string") return;
  
    const metricName = metrics[index].name;
    const confirmDelete = window.confirm(`Are you sure you want to delete "${metricName}"?`);
    if (!confirmDelete) return;
  
    try {
      const response = await fetch(`http://localhost:8016/projects/deleteProjectMetrics`, {
        method: "POST",
        credentials: 'include',
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          project_name: projectName,
          metric: metricName,
        }),
      });
  
      const data = await response.json();
      console.log("Delete response:", data);
  
      if (response.ok && data.message === "Project metric deleted successfully") {
        fetchMetrics();
      } else {
        alert(data.error || "Failed to delete metric");
      }
    } catch (error) {
      console.error("Error deleting metric:", error);
      alert("An error occurred while deleting the metric.");
    }
  };

  const handleClose = () => {
    setModalOpen(false);
    setEditingIndex(null);
    resetForm();
  };

  const resetForm = () => {
    setForm({
      name: "",
      minValue: 1,
      maxValue: 5,
      minLabel: "",
      maxLabel: "",
      description: "",
      value: 3,
    });
  };

  if (!projectName || typeof projectName !== "string") return null;

  return (
    <RoleCheck requiredRole="researcher">
      <div>
        <Navbar />
        <Box display="flex" height="100vh">
          <Box width="250px" flexShrink={0}>
            <Sidebar project_name={projectName} />
          </Box>

          <Box flex={1} p={4} overflow="auto">
            <Box mt={4}>
              <Button
                variant="contained"
                sx={{
                  boxShadow: 2,
                  backgroundColor: '#282d3f',
                  '&:hover': {
                    backgroundColor: '#1a1f2e',
                  }
                }}
                onClick={() => {
                  resetForm();
                  setEditingIndex(null);
                  setModalOpen(true);
                }}
              >
                + Create New Metric
              </Button>
            </Box>

            <Box mt={4}>
              {metrics.map((metric, index) => (
                <Box
                  key={index}
                  p={2}
                  border={1}
                  borderRadius={2}
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  mb={2}
                >
                  <Box flex={1} pr={2}>
                    <Typography variant="h6">{metric.name}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      {metric.description}
                    </Typography>
                    <Box width="100%">
                      {/* <Slider
                        min={metric.minValue}
                        max={metric.maxValue}
                        value={metric.value}
                        disabled
                        valueLabelDisplay="auto"
                        sx={{
                          color: '#282d3f',
                          '& .MuiSlider-thumb': {
                            backgroundColor: '#282d3f',
                          },
                          '& .MuiSlider-track': {
                            backgroundColor: '#282d3f',
                          },
                          '& .MuiSlider-rail': {
                            backgroundColor: '#b0b0b0',
                          },
                        }}
                      /> */}
                      <Slider
                        min={metric.minValue}
                        max={metric.maxValue}
                        defaultValue={metric.value}
                        valueLabelDisplay="auto"
                        onChange={() => {}}
                        sx={{
                          color: '#282d3f',
                          '& .MuiSlider-thumb': {
                            backgroundColor: '#282d3f',
                          },
                          '& .MuiSlider-track': {
                            backgroundColor: '#282d3f',
                          },
                          '& .MuiSlider-rail': {
                            backgroundColor: '#b0b0b0',
                          },
                        }}
                      />
                    </Box>
                    <Typography>
                      {metric.minLabel} ({metric.minValue}) - {metric.maxLabel} ({metric.maxValue})
                    </Typography>
                  </Box>
                  <Box display="flex" flexDirection="column" gap={1}>
                    <Button variant="contained" onClick={() => handleEdit(index)}>Edit</Button>
                    <Button variant="contained" color="error" onClick={() => handleDelete(index)}>Delete</Button>
                  </Box>
                </Box>
              ))}
            </Box>

            <Dialog open={modalOpen} onClose={handleClose}>
              <DialogTitle>{editingIndex !== null ? "Edit Metric" : "Add Metric"}</DialogTitle>
              <DialogContent>
                <Box display="flex" flexDirection="column" gap={2}>
                  <TextField
                    name="name"
                    label="Metric Name"
                    value={form.name}
                    onChange={handleInputChange}
                    disabled={editingIndex !== null}
                  />
                  <TextField name="minValue" type="number" label="Minimum Value" value={form.minValue} onChange={handleInputChange} />
                  <TextField name="maxValue" type="number" label="Maximum Value" value={form.maxValue} onChange={handleInputChange} />
                  <TextField name="minLabel" label="Minimum Label" value={form.minLabel} onChange={handleInputChange} />
                  <TextField name="maxLabel" label="Maximum Label" value={form.maxLabel} onChange={handleInputChange} />
                  <TextField name="description" label="Description" value={form.description} onChange={handleInputChange} />
                  <Button
                    variant="contained"
                    onClick={handleSave}
                    sx={{
                      boxShadow: 2,
                      backgroundColor: '#282d3f',
                      '&:hover': {
                        backgroundColor: '#1a1f2e',
                      }
                    }}
                  >
                    Save
                  </Button>
                </Box>
              </DialogContent>
            </Dialog>
          </Box>
        </Box>
      </div>
    </RoleCheck>
  );
};

export default MetricsPage;
