import React, { useState, ChangeEvent } from "react";
import { Button, Dialog, DialogTitle, DialogContent, TextField, Slider, Box, Typography } from "@mui/material";
import Navbar from "components/nav_bar_researcher";
import Sidebar from "components/project_sidebar"

interface Metric {
  name: string;
  minValue: number;
  maxValue: number;
  minLabel: string;
  maxLabel: string;
  description: string;
  value: number;
}

const defaultMetrics: Metric[] = [
  {
    name: "Naturalness",
    minValue: 1,
    maxValue: 5,
    minLabel: "Completely unlike a human",
    maxLabel: "Human like",
    description: "How human like is the speech in the clip?",
    value: 3,
  },
  {
    name: "Clarity",
    minValue: 1,
    maxValue: 5,
    minLabel: "Unclear",
    maxLabel: "Clear",
    description: "How would you rate this clip by Legibility",
    value: 3,
  },
  {
    name: "Intelligibility",
    minValue: 1,
    maxValue: 5,
    minLabel: "Didn't catch any words",
    maxLabel: "Understood everything said",
    description: "How much did you understand what the speaker is saying?",
    value: 3,
  },
];

const MetricsPage = () => {
  const [metrics, setMetrics] = useState<Metric[]>(defaultMetrics);
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

  const handleSliderChange = (index: number, val: number | number[]) => {
    const newValue = Array.isArray(val) ? val[0] : val;
    setMetrics((prevMetrics) =>
      prevMetrics.map((metric, i) =>
        i === index ? { ...metric, value: newValue } : metric
      )
    );
  };

  const handleSave = () => {
    if (editingIndex !== null) {
      setMetrics((prevMetrics) => {
        const updatedMetrics = [...prevMetrics];
        updatedMetrics[editingIndex] = { ...form, value: form.minValue };
        return updatedMetrics;
      });
    } else {
      setMetrics((prevMetrics) => [...prevMetrics, { ...form, value: form.minValue }]);
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

  return (
    <div>
      <Navbar />
      <Box display="flex" height="100vh">
        {/* Sidebar with fixed width */}
        <Box width="250px" flexShrink={0}>
          <Sidebar project_name="Project_4" />
        </Box>
  
        {/* Main content that doesn't get blocked */}
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
                    <Slider
                      min={metric.minValue}
                      max={metric.maxValue}
                      value={metric.value}
                      onChange={(_, val) => handleSliderChange(index, val)}
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
                    />
                  </Box>
                  <Typography>
                    {metric.minLabel} ({metric.minValue}) - {metric.maxLabel} ({metric.maxValue})
                  </Typography>
                </Box>
                <Button variant="outlined" onClick={() => handleEdit(index)}>
                  Edit
                </Button>
              </Box>
            ))}
          </Box>
  
          {/* Metric Add/Edit Modal */}
          <Dialog open={modalOpen} onClose={handleClose}>
            <DialogTitle>{editingIndex !== null ? "Edit Metric" : "Add Metric"}</DialogTitle>
            <DialogContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <TextField name="name" label="Metric Name" value={form.name} onChange={handleInputChange} />
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
                  }}>
                  Save
                </Button>
              </Box>
            </DialogContent>
          </Dialog>
        </Box>
      </Box>
    </div>
  );
  
};

export default MetricsPage;
