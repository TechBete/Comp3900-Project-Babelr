import { useEffect, useState } from "react";
import RoleCheck from "components/role_checker";
import Navbar from "components/nav_bar_researcher";
	import {
	Container,
	Typography,
	Card,
	CardContent,
	List,
	ListItem,
	ListItemText,
	Divider,
	Box,
	Button,
	Dialog,
	DialogTitle,
	DialogContent,
	DialogActions,
	TextField,
	Alert,
	FormControl,
	MenuItem,
	InputLabel,
	Select
} from "@mui/material";

type ResearcherData = {
	Uuid: string;
	"First Name": string;
	"Last Name": string;
	Email: string;
	Password: string;
	"Date of Birth": string;
	Gender: string;
	Country: string;
	Education: string;
	Organisation: string;
};

export default function ResearcherProfilePage() {
	const [researcherData, setResearcherData] = useState<ResearcherData | null>(null);

	// Password modal state
	const [isPasswordEditOpen, setIsPasswordEditOpen] = useState(false);
	const [newPassword, setNewPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [errorMsg, setErrorMsg] = useState<string | null>(null);
	const [successMsg, setSuccessMsg] = useState<string | null>(null);

	// Personal info modal state
	const [isPersonalInfoEditOpen, setIsPersonalInfoEditOpen] = useState(false);
	const [firstName, setFirstName] = useState("");
	const [lastName, setLastName] = useState("");
	const [dateOfBirth, setDateOfBirth] = useState("");
	const [gender, setGender] = useState("");
	const [country, setCountry] = useState("");
	const [education, setEducation] = useState("");
	const [organisation, setOrganisation] = useState("");
	
	useEffect(() => {
		getResearcherData();
	}, []);

	async function getResearcherData() {
		try {
		const response = await fetch("http://localhost:8016/researcher/getResearcher", {
			method: "GET",
			credentials: "include",
		});

		if (response.ok) {
			const data = await response.json();
			console.log("Fetched researcher data:", data); // Debugging the fetched data
			setResearcherData(data);
		} else {
			const error = await response.json();
			console.error("Error fetching listener data:", error);
		}
		} catch (err) {
		console.error("Network error:", err);
		}
	}

	// Open password edit modal
	const handlePasswordEditOpen = () => {
		setIsPasswordEditOpen(true);
		setNewPassword("");
		setConfirmPassword("");
		setErrorMsg(null);
		setSuccessMsg(null);
	};

	// Close password edit modal
	const handlePasswordEditClose = () => setIsPasswordEditOpen(false);

	// Save the new password
	const handlePasswordSave = async () => {
		if (!newPassword || !confirmPassword) {
		setErrorMsg("Both fields are required.");
		return;
		}

		if (newPassword !== confirmPassword) {
		setErrorMsg("Passwords do not match.");
		return;
		}

		try {
		const res = await fetch("http://localhost:8016/auth/userResetPassword", {
			method: "POST",
			credentials: "include",
			headers: {
			"Content-Type": "application/json",
			},
			body: JSON.stringify({ pw: newPassword, pw_confirmation: confirmPassword }),
		});

		const result = await res.json();

		if (res.ok) {
			setSuccessMsg("Password updated successfully.");
			setErrorMsg(null);
			setTimeout(() => {
			setIsPasswordEditOpen(false);
			}, 1500);
		} else {
			setErrorMsg(result.error || "Failed to update password.");
			setSuccessMsg(null);
		}
		} catch (err) {
			console.error("Error updating password:", err);
			setErrorMsg("Server error occurred.");
		}
	};

	const handlePersonalInfoEditOpen = () => {
		if (!researcherData) return;
		setIsPersonalInfoEditOpen(true);
		setFirstName(researcherData["First Name"]);
		setLastName(researcherData["Last Name"]);
		setDateOfBirth(researcherData["Date of Birth"]);
		setGender(researcherData.Gender?.replace("Gender.", "") || "");
		setCountry(researcherData["Country"]);
		setEducation(researcherData.Education);
		setOrganisation(researcherData.Organisation);
	};

	const handlePersonalInfoEditClose = () => {
		setIsPersonalInfoEditOpen(false);
	};

	const handlePersonalInfoSave = async () => {
		if (!firstName || !lastName || !dateOfBirth || !gender || !country || !education || !organisation) {
			alert("Please fill in all fields before saving.");
		return;
		}

		try {
		const res = await fetch("http://localhost:8016/researcher/updateResearcherProfile", {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
			first_name: firstName,
			last_name: lastName,
			date_of_birth: dateOfBirth,
			country_of_residence: country,
			education: education,
			gender: gender,
			organisation: organisation,
			}),
		});

		const result = await res.json();

		if (res.ok) {
			setIsPersonalInfoEditOpen(false);
			getResearcherData();
		} else {
			alert(result.error || "Error saving personal info");
		}
		} catch (err) {
			console.error("Error saving personal info:", err);
			alert("Server error occurred.");
		}
	};

	return (
		<RoleCheck requiredRole="researcher">
		<Navbar />
		<Container sx={{ maxWidth: "700px !important" }}>
			<Box mt={12} display="flex" flexDirection="column" gap={4} pb={4}>
			<Typography variant="h4" fontWeight="bold" gutterBottom>
				Profile
			</Typography>

			{!researcherData ? (
				<Typography>Loading...</Typography>
			) : (
				<>
				{/* User Details */}
				<Card>
					<CardContent>
					<Box display="flex" justifyContent="space-between" mb={2}>
						<Typography variant="h6">User Details</Typography>
						<Button 
						size="small" 
						sx={{
							color: "#2b4450",
							"&:hover": {
							backgroundColor: "rgba(43, 68, 80, 0.08)", 
							},
						}}
						onClick={handlePasswordEditOpen}>
							Update Password
						</Button>
					</Box>
					<Divider sx={{ mb: 2 }} />
					<List>
						<ListItem>
						<ListItemText primary="Email" secondary={researcherData["Email"]} />
						</ListItem>
						<ListItem>
						<ListItemText primary="Password" secondary="**********" />
						</ListItem>
					</List>
					</CardContent>
				</Card>

				{/* Personal Info */}
				<Card>
					<CardContent>
					<Box display="flex" justifyContent="space-between" mb={2}>
					<Typography variant="h6">Personal Info</Typography>
					<Button 
						size="small" 
						sx={{
						color: "#2b4450",
						"&:hover": {
							backgroundColor: "rgba(43, 68, 80, 0.08)", 
						},
						}}
						onClick={handlePersonalInfoEditOpen}>
						Edit Info
					</Button>
					</Box>
					<Divider sx={{ mb: 2 }} />
					<List>
						<ListItem>
						<ListItemText primary="First Name" secondary={researcherData["First Name"]} />
						</ListItem>
						<ListItem>
						<ListItemText primary="Last Name" secondary={researcherData["Last Name"]} />
						</ListItem>
						<ListItem>
						<ListItemText primary="Date of Birth" secondary={researcherData["Date of Birth"]} />
						</ListItem>
						<ListItem>
						<ListItemText
							primary="Gender"
							secondary={researcherData["Gender"]?.replace("Gender.", "") || "Not specified"}
						/>
						</ListItem>
						<ListItem>
						<ListItemText primary="Country of Residence" secondary={researcherData["Country"]} />
						</ListItem>
						<ListItem>
						<ListItemText primary="Education" secondary={researcherData["Education"]} />
						</ListItem>
						<ListItem>
						<ListItemText primary="Organisation" secondary={researcherData["Organisation"]} />
						</ListItem>
					</List>
					</CardContent>
				</Card>
				</>
			)}

			{/* Password Edit Modal */}
			<Dialog open={isPasswordEditOpen} onClose={handlePasswordEditClose} fullWidth maxWidth="sm">
				<DialogTitle sx={{ pt: 4 }}>Update Password</DialogTitle>
				<DialogContent>
				{errorMsg && <Alert severity="error" sx={{ mb: 2 }}>{errorMsg}</Alert>}
				{successMsg && <Alert severity="success" sx={{ mb: 2 }}>{successMsg}</Alert>}
				<TextField
					label="New Password"
					type="password"
					fullWidth
					margin="dense"
					value={newPassword}
					onChange={(e) => setNewPassword(e.target.value)}
					sx={{ mt: 2 }}
				/>
				<TextField
					label="Confirm Password"
					type="password"
					fullWidth
					margin="dense"
					value={confirmPassword}
					onChange={(e) => setConfirmPassword(e.target.value)}
					sx={{ mt: 2 }}
				/>
				</DialogContent>
				<DialogActions sx={{ pb: 3, px: 3 }}>
				<Button 
					sx={{
					color: "#2b4450",
					"&:hover": {
						backgroundColor: "rgba(43, 68, 80, 0.08)", 
					},
					}}
					onClick={handlePasswordEditClose}>
					Cancel
				</Button>
				<Button 
					variant="contained" 
					sx={{
					backgroundColor: "#2b4450",
					"&:hover": {
						backgroundColor: "#1f333c",
					},
					}} 
					onClick={handlePasswordSave}>
					Save
				</Button>
				</DialogActions>
			</Dialog>
			
			{/* Personal Info Edit Modal */}
			<Dialog
				open={isPersonalInfoEditOpen}
				onClose={handlePersonalInfoEditClose}
				fullWidth
				maxWidth="sm"
				sx={{ "& .MuiDialog-paper": { minHeight: 690 } }}
			>
				<DialogTitle sx={{ pt: 4 }}>Edit Personal Info</DialogTitle>
				<DialogContent>
				<TextField
					label="First Name"
					fullWidth
					value={firstName}
					onChange={(e) => setFirstName(e.target.value)}
					sx={{ mt: 2 }}
				/>
				<TextField
					label="Last Name"
					fullWidth
					value={lastName}
					onChange={(e) => setLastName(e.target.value)}
					sx={{ mt: 2 }}
				/>
				<TextField
					label="Date of Birth"
					fullWidth
					value={dateOfBirth}
					onChange={(e) => setDateOfBirth(e.target.value)}
					sx={{ mt: 2 }}
				/>
				{/* Gender Dropdown */}
				<FormControl fullWidth margin="dense" sx={{ mt: 2 }}>
					<InputLabel id="gender-label">Gender</InputLabel>
					<Select
					labelId="gender-label"
					id="gender-select"
					value={gender}
					label="Gender"
					onChange={(e) => setGender(e.target.value)}
					>
					<MenuItem value="male">Male</MenuItem>
					<MenuItem value="female">Female</MenuItem>
					<MenuItem value="other">Other</MenuItem>
					</Select>
				</FormControl>
				<TextField
					label="Country"
					fullWidth
					value={country}
					onChange={(e) => setCountry(e.target.value)}
					sx={{ mt: 2 }}
				/>
				<TextField
					label="Education"
					fullWidth
					value={education}
					onChange={(e) => setEducation(e.target.value)}
					sx={{ mt: 2 }}
				/>
				<TextField
					label="Organisation"
					fullWidth
					value={organisation}
					onChange={(e) => setOrganisation(e.target.value)}
					sx={{ mt: 2 }}
				/>
				</DialogContent>
				<DialogActions sx={{ p: 0, pb: 3, px: 3 }}>
				<Button 
					sx={{
					color: "#2b4450",
					"&:hover": {
						backgroundColor: "rgba(43, 68, 80, 0.08)", 
					},
					}}
					onClick={handlePersonalInfoEditClose}>
					Cancel
				</Button>
				<Button 
					variant="contained" 
					sx={{
					backgroundColor: "#2b4450",
					"&:hover": {
						backgroundColor: "#1f333c",
					},
					}} 
					onClick={handlePersonalInfoSave}>
					Save
				</Button>
				</DialogActions>
			</Dialog>
			</Box>
		</Container>
		</RoleCheck>
	);
}
