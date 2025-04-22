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
  "Project List": string[];
};

export default function ResearcherProfilePage() {
  const [researcherData, setResearcherData] = useState<ResearcherData | null>(null);

  const [isPasswordEditOpen, setIsPasswordEditOpen] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [isInfoEditOpen, setIsInfoEditOpen] = useState(false);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [gender, setGender] = useState("");
  const [country, setCountry] = useState("");
  const [education, setEducation] = useState("");
  const [organisation, setOrganisation] = useState("");

  useEffect(() => {
    fetchResearcherData();
  }, []);

  async function fetchResearcherData() {
    try {
      const response = await fetch("http://localhost:8016/researcher/getResearcher", {
        method: "GET",
        credentials: "include",
      });

      if (response.ok) {
        const data: ResearcherData = await response.json();
        setResearcherData(data);
      } else {
        console.error("Failed to fetch researcher data.");
      }
    } catch (err) {
      console.error("Fetch error:", err);
    }
  }

  const handlePasswordSave = async () => {
    if (!newPassword || !confirmPassword) {
      setErrorMsg("Both fields are required.");
      return;
    }

    try {
      const res = await fetch("http://localhost:8016/auth/userResetPassword", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pw: newPassword, pw_confirmation: confirmPassword }),
      });

      const result = await res.json();

      if (res.ok) {
        setSuccessMsg("Password updated.");
        setTimeout(() => setIsPasswordEditOpen(false), 1500);
      } else {
        setErrorMsg(result.error || "Failed to update password.");
      }
    } catch (err) {
      console.error("Password error:", err);
      setErrorMsg("Server error occurred.");
    }
  };

  const handleInfoSave = async () => {
    if (!firstName || !lastName || !dateOfBirth || !gender || !country || !education || !organisation) {
      alert("Please fill in all fields.");
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
          gender,
          country,
          education,
          organisation,
        }),
      });

      const result = await res.json();

      if (res.ok) {
        setIsInfoEditOpen(false);
        fetchResearcherData();
      } else {
        alert(result.error || "Failed to update info.");
      }
    } catch (err) {
      console.error("Info save error:", err);
      alert("Server error occurred.");
    }
  };

  const openEditInfo = () => {
    if (!researcherData) return;
    setFirstName(researcherData["First Name"]);
    setLastName(researcherData["Last Name"]);
    setDateOfBirth(researcherData["Date of Birth"]);
    setGender(researcherData.Gender);
    setCountry(researcherData.Country);
    setEducation(researcherData.Education);
    setOrganisation(researcherData.Organisation);
    setIsInfoEditOpen(true);
  };

  return (
    <RoleCheck requiredRole="researcher">
      <Navbar />
      <Container sx={{ maxWidth: "700px !important" }}>
        <Box mt={12} display="flex" flexDirection="column" gap={4} pb={4}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Researcher Profile
          </Typography>

          {!researcherData ? (
            <Typography>Loading...</Typography>
          ) : (
            <>
              {/* Account Info */}
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" mb={2}>
                    <Typography variant="h6">Account</Typography>
                    <Button size="small" onClick={() => setIsPasswordEditOpen(true)}>Update Password</Button>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <List>
                    <ListItem><ListItemText primary="Email" secondary={researcherData.Email} /></ListItem>
                    <ListItem><ListItemText primary="Password" secondary="**********" /></ListItem>
                  </List>
                </CardContent>
              </Card>

              {/* Personal Info */}
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" mb={2}>
                    <Typography variant="h6">Personal Info</Typography>
                    <Button size="small" onClick={openEditInfo}>Edit Info</Button>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <List>
                    <ListItem><ListItemText primary="First Name" secondary={researcherData["First Name"]} /></ListItem>
                    <ListItem><ListItemText primary="Last Name" secondary={researcherData["Last Name"]} /></ListItem>
                    <ListItem><ListItemText primary="Date of Birth" secondary={researcherData["Date of Birth"]} /></ListItem>
                    <ListItem><ListItemText primary="Gender" secondary={researcherData.Gender} /></ListItem>
                    <ListItem><ListItemText primary="Country" secondary={researcherData.Country} /></ListItem>
                    <ListItem><ListItemText primary="Education" secondary={researcherData.Education} /></ListItem>
                    <ListItem><ListItemText primary="Organisation" secondary={researcherData.Organisation} /></ListItem>
                  </List>
                </CardContent>
              </Card>

              {/* Password Dialog */}
              <Dialog open={isPasswordEditOpen} onClose={() => setIsPasswordEditOpen(false)} fullWidth maxWidth="sm">
                <DialogTitle>Update Password</DialogTitle>
                <DialogContent>
                  {errorMsg && <Alert severity="error">{errorMsg}</Alert>}
                  {successMsg && <Alert severity="success">{successMsg}</Alert>}
                  <TextField label="New Password" type="password" fullWidth margin="dense" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
                  <TextField label="Confirm Password" type="password" fullWidth margin="dense" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
                </DialogContent>
                <DialogActions>
                  <Button onClick={() => setIsPasswordEditOpen(false)}>Cancel</Button>
                  <Button variant="contained" onClick={handlePasswordSave}>Save</Button>
                </DialogActions>
              </Dialog>

              {/* Info Edit Dialog */}
              <Dialog open={isInfoEditOpen} onClose={() => setIsInfoEditOpen(false)} fullWidth maxWidth="sm">
                <DialogTitle>Edit Personal Info</DialogTitle>
                <DialogContent>
                  <TextField label="First Name" fullWidth margin="dense" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
                  <TextField label="Last Name" fullWidth margin="dense" value={lastName} onChange={(e) => setLastName(e.target.value)} />
                  <TextField label="Date of Birth" fullWidth margin="dense" value={dateOfBirth} onChange={(e) => setDateOfBirth(e.target.value)} />
                  <TextField label="Gender" fullWidth margin="dense" value={gender} onChange={(e) => setGender(e.target.value)} />
                  <TextField label="Country" fullWidth margin="dense" value={country} onChange={(e) => setCountry(e.target.value)} />
                  <TextField label="Education" fullWidth margin="dense" value={education} onChange={(e) => setEducation(e.target.value)} />
                  <TextField label="Organisation" fullWidth margin="dense" value={organisation} onChange={(e) => setOrganisation(e.target.value)} />
                </DialogContent>
                <DialogActions>
                  <Button onClick={() => setIsInfoEditOpen(false)}>Cancel</Button>
                  <Button variant="contained" onClick={handleInfoSave}>Save</Button>
                </DialogActions>
              </Dialog>
            </>
          )}
        </Box>
      </Container>
    </RoleCheck>
  );
}
