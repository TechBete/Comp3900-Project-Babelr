import React, { useState, ChangeEvent, useEffect } from "react";
import { useRouter } from "next/router";
import {
  	Button, 
	Dialog, 
	DialogTitle, 
	DialogContent,
  	TextField, 
	Slider, 
	Box, 
	Typography
} from "@mui/material";
import Navbar from "components/nav_bar_researcher";
import Sidebar from "components/project_sidebar";
import RoleCheck from "components/role_checker";
import styles from "stylesheets/researcher_metrics.module.css";

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
	const [formErrors, setFormErrors] = useState<Record<string, string>>({});
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
	// getting existing metrics from the backend
	const fetchMetrics = async () => {
		if (!projectName || typeof projectName !== "string") return;

		const response = await fetch(`http://localhost:8016/projects/getProjectMetrics`, {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ project_name: projectName }),
		});

		const data = await response.json();

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
		setMetrics(parsedMetrics);
		}
	};
	// only fetches after getting the porject name 
	useEffect(() => {
		fetchMetrics();
	}, [projectName]);

	// when a metric is either added or updated
	const handleSave = async () => {
		if (!projectName || typeof projectName !== "string") return;
		// error checking
		const errors: Record<string, string> = {};
		if (!form.name.trim()) errors.name = "Metric name is required";
		if (!form.minLabel.trim()) errors.minLabel = "Minimum label is required";
		if (!form.maxLabel.trim()) errors.maxLabel = "Maximum label is required";
		if (!form.description.trim()) errors.description = "Description is required";
		if (form.minValue === null || form.minValue === undefined) errors.minValue = "Minimum value is required";
		if (form.maxValue === null || form.maxValue === undefined) errors.maxValue = "Maximum value is required";
		if (form.minValue >= form.maxValue) errors.minValue = "Min must be less than Max";
	
		setFormErrors(errors);
	
		if (Object.keys(errors).length > 0) return;
		// checks for duplicate metric names
		const existingNames = metrics.map((m) => m.name.toLowerCase());
		if (editingIndex === null && existingNames.includes(form.name.toLowerCase())) {
		setFormErrors({ name: "A metric with this name already exists" });
		return;
		}
		// picks the API call depending on whether the metric is being edited or created
		const url = editingIndex !== null
		? `http://localhost:8016/projects/updateProjectMetrics`
		: `http://localhost:8016/projects/setProjectMetricField`;
	
		const response = await fetch(url, {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
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
		if (data.metrics) fetchMetrics();
	
		setModalOpen(false);
		setEditingIndex(null);
		resetForm();
	};
	

	const handleEdit = (index: number) => {
		setForm(metrics[index]);
		setEditingIndex(index);
		setModalOpen(true);
	};
  // deleting a metric
	const handleDelete = async (index: number) => {
		if (!projectName || typeof projectName !== "string") return;

		const metricName = metrics[index].name;
		const confirmDelete = window.confirm(`Are you sure you want to delete "${metricName}"?`);
		if (!confirmDelete) return;

		const response = await fetch(`http://localhost:8016/projects/deleteProjectMetrics`, {
		method: "POST",
		credentials: "include",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			project_name: projectName,
			metric: metricName,
		}),
		});

		const data = await response.json();
		if (response.ok && data.message === "Project metric deleted successfully") {
		fetchMetrics();
		} else {
		alert(data.error || "Failed to delete metric");
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
    	setFormErrors({});
  	};

  	if (!projectName || typeof projectName !== "string") return null;

	return (
		<RoleCheck requiredRole="researcher">
		<div>
			<Navbar />
			<Box className={styles.container}>
			<Box className={styles.sidebar}>
				<Sidebar project_name={projectName} />
			</Box>
			
			<Box className={styles.content}>
				<Box display="flex" justifyContent="space-between" alignItems="center" mb={2} mt={5}>
				<Typography variant="h4" gutterBottom>
					Metrics Dashboard
				</Typography>
				<Button
					variant="contained"
					className={styles.createButton}
					onClick={() => {
					resetForm();
					setEditingIndex(null);
					setModalOpen(true);
					}}
				>
					+ Create New Metric
				</Button>
				</Box>
				{/* displays the metrics  */}
				<Box mt={4}>
				{metrics.map((metric, index) => (
					<Box key={index} className={styles.metricCard}>
					<Box className={styles.metricDetails}>
						<Typography variant="h6">{metric.name}</Typography>
						<Typography variant="body2" color="textSecondary">
						{metric.description}
						</Typography>
						<Box width="100%">
						<Slider
							min={metric.minValue}
							max={metric.maxValue}
							defaultValue={metric.maxValue}
							valueLabelDisplay="auto"
							onChange={() => {}}
							className={styles.slider}
						/>
						</Box>
						<Typography>
						{metric.minLabel} ({metric.minValue}) - {metric.maxLabel} ({metric.maxValue})
						</Typography>
					</Box>
					{/* edit and delete buttons */}
					<Box className={styles.actionButtons}>
						<Button variant="contained" onClick={() => handleEdit(index)}>Edit</Button>
						<Button variant="contained" color="error" onClick={() => handleDelete(index)}>Delete</Button>
					</Box>
					</Box>
				))}
				</Box>
				{/* editing and creating metric modal */}
				<Dialog open={modalOpen} onClose={handleClose}>
				<DialogTitle>{editingIndex !== null ? "Edit Metric" : "Add Metric"}</DialogTitle>
				<DialogContent>
					<Box className={styles.dialogForm}>
					<TextField
						name="name"
						label="Metric Name"
						value={form.name}
						onChange={handleInputChange}
						error={!!formErrors.name}
						helperText={formErrors.name}
						disabled={editingIndex !== null}
					/>
					<TextField
						name="minValue"
						type="number"
						label="Minimum Value"
						value={form.minValue}
						onChange={handleInputChange}
						error={!!formErrors.minValue}
						helperText={formErrors.minValue}
					/>
					<TextField
						name="maxValue"
						type="number"
						label="Maximum Value"
						value={form.maxValue}
						onChange={handleInputChange}
						error={!!formErrors.maxValue}
						helperText={formErrors.maxValue}
					/>
					<TextField
						name="minLabel"
						label="Minimum Label"
						value={form.minLabel}
						onChange={handleInputChange}
						error={!!formErrors.minLabel}
						helperText={formErrors.minLabel}
					/>
					<TextField
						name="maxLabel"
						label="Maximum Label"
						value={form.maxLabel}
						onChange={handleInputChange}
						error={!!formErrors.maxLabel}
						helperText={formErrors.maxLabel}
					/>
					<TextField
						name="description"
						label="Description"
						value={form.description}
						onChange={handleInputChange}
						error={!!formErrors.description}
						helperText={formErrors.description}
					/>
					<Button
						variant="contained"
						className={styles.createButton}
						onClick={handleSave}
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