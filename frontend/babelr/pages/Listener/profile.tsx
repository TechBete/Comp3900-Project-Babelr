import { useEffect, useState } from "react";
import RoleCheck from "components/role_checker";
import Navbar from "components/nav_bar_listener";
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
  MenuItem,
  InputLabel,
  Select,
  FormControl,
} from "@mui/material";

type LanguageEntry = {
  language: string;
  proficiency: string;
};

type ListenerData = {
  Uuid: string;
  "First Name": string;
  "Last Name": string;
  Email: string;
  Password: string;
  "Reward Points": number;
  "Background Info": string;
  "Date of Birth": string;
  Gender: string;
  "Country of Residence": string;
  Education: string;
  languages: LanguageEntry[][];
};

const proficiencyOptions: { [key: string]: string } = {
  native: "Native",
  bilingual: "Bilingual",
  fluent: "Fluent",
  professional: "Professional",
  limited_working: "Limited Working",
  elementary: "Elementary",
};

export default function ProfilePage() {
  const [listenerData, setListenerData] = useState<ListenerData | null>(null);

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
  const [backgroundInfo, setBackgroundInfo] = useState("");

  // Language edit modal state
  const [isLanguageEditOpen, setIsLanguageEditOpen] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("");
  const [newProficiency, setNewProficiency] = useState("");

  useEffect(() => {
    getListenerData();
  }, []);

  async function getListenerData() {
    try {
      const response = await fetch("http://localhost:8016/listener/getListener", {
        method: "GET",
        credentials: "include",
      });

      if (response.ok) {
        const data: ListenerData = await response.json();
        setListenerData(data);
      } else {
        const error = await response.json();
        console.error("Error fetching listener data:", error);
      }
    } catch (err) {
      console.error("Network error:", err);
    }
  }

  const handlePasswordEditOpen = () => {
    setIsPasswordEditOpen(true);
    setNewPassword("");
    setConfirmPassword("");
    setErrorMsg(null);
    setSuccessMsg(null);
  };
  const handlePasswordEditClose = () => setIsPasswordEditOpen(false);

  const handlePasswordSave = async () => {
    if (!newPassword || !confirmPassword) {
      setErrorMsg("Both fields are required.");
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
    if (!listenerData) return;
    setIsPersonalInfoEditOpen(true);
    setFirstName(listenerData["First Name"]);
    setLastName(listenerData["Last Name"]);
    setDateOfBirth(listenerData["Date of Birth"]);
    setGender(listenerData.Gender || "");
    setCountry(listenerData["Country of Residence"]);
    setEducation(listenerData.Education);
    setBackgroundInfo(listenerData["Background Info"]);
  };

  const handlePersonalInfoEditClose = () => {
    setIsPersonalInfoEditOpen(false);
  };

  const handlePersonalInfoSave = async () => {
    if (!firstName || !lastName || !dateOfBirth || !gender || !country || !education || !backgroundInfo) {
      alert("Please fill in all fields before saving.");
      return;
    }
  
    try {
      const res = await fetch("http://localhost:8016/listener/changeDemographics", {
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
          background_info: backgroundInfo,
        }),
      });

      const result = await res.json();

      if (res.ok) {
        setIsPersonalInfoEditOpen(false);
        getListenerData();
      } else {
        alert(result.error || "Error saving personal info");
      }
    } catch (err) {
      console.error("Error saving personal info:", err);
      alert("Server error occurred.");
    }
  };

  const handleLanguageEditOpen = (language: string, proficiency: string) => {
    setSelectedLanguage(language);
    setNewProficiency(proficiency);
    setIsLanguageEditOpen(true);
  };

  const handleLanguageEditClose = () => {
    setIsLanguageEditOpen(false);
    setSelectedLanguage("");
    setNewProficiency("");
  };

  const handleLanguageSave = async () => {
    try {
      const res = await fetch("http://localhost:8016/listener/editLanguage", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          language: selectedLanguage,
          new_proficiency: newProficiency,
        }),
      });

      const result = await res.json();

      if (res.ok) {
        handleLanguageEditClose();
        getListenerData();
      } else {
        alert(result.error || "Failed to update language.");
      }
    } catch (err) {
      console.error("Error updating language:", err);
      alert("Server error occurred.");
    }
  };

  return (
    <RoleCheck requiredRole="listener">
      <Navbar />
      <Container sx={{ maxWidth: "700px !important" }}>
        <Box mt={12} display="flex" flexDirection="column" gap={4} pb={4}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Profile
          </Typography>

          {!listenerData ? (
            <Typography>Loading...</Typography>
          ) : (
            <>
              {/* User Details */}
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" mb={2}>
                    <Typography variant="h6">User Details</Typography>
                    <Button size="small" onClick={handlePasswordEditOpen}>Update Password</Button>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <List>
                    <ListItem><ListItemText primary="Email" secondary={listenerData.Email} /></ListItem>
                    <ListItem><ListItemText primary="Password" secondary="**********" /></ListItem>
                    <ListItem><ListItemText primary="Reward Points" secondary={listenerData["Reward Points"]} /></ListItem>
                  </List>
                </CardContent>
              </Card>

              {/* Personal Info */}
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" mb={2}>
                    <Typography variant="h6">Personal Info</Typography>
                    <Button size="small" onClick={handlePersonalInfoEditOpen}>Edit Info</Button>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <List>
                    <ListItem><ListItemText primary="First Name" secondary={listenerData["First Name"]} /></ListItem>
                    <ListItem><ListItemText primary="Last Name" secondary={listenerData["Last Name"]} /></ListItem>
                    <ListItem><ListItemText primary="Date of Birth" secondary={listenerData["Date of Birth"]} /></ListItem>
                    <ListItem><ListItemText primary="Gender" secondary={listenerData.Gender || "Not specified"} /></ListItem>
                    <ListItem><ListItemText primary="Country of Residence" secondary={listenerData["Country of Residence"]} /></ListItem>
                    <ListItem><ListItemText primary="Education" secondary={listenerData.Education} /></ListItem>
                    <ListItem><ListItemText primary="Background Info" secondary={listenerData["Background Info"]} /></ListItem>
                  </List>
                </CardContent>
              </Card>

              {/* Languages */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Languages</Typography>
                  <Divider sx={{ mb: 2 }} />
                  <List>
                    {listenerData.languages[0]?.map((lang, idx) => (
                      <ListItem key={idx} secondaryAction={
                        <Button size="small" onClick={() => handleLanguageEditOpen(lang.language, lang.proficiency)}>Edit</Button>
                      }>
                        <ListItemText
                          primary={lang.language}
                          secondary={`Proficiency: ${proficiencyOptions[lang.proficiency] || lang.proficiency}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
              
              {/* Password Modal */}
              <Dialog open={isPasswordEditOpen} onClose={handlePasswordEditClose} fullWidth maxWidth="sm">
                <DialogTitle sx={{ pt: 4 }}>Update Password</DialogTitle>
                <DialogContent>
                  {errorMsg && <Alert severity="error" sx={{ mb: 2 }}>{errorMsg}</Alert>}
                  {successMsg && <Alert severity="success" sx={{ mb: 2 }}>{successMsg}</Alert>}
                  <TextField label="New Password" type="password" fullWidth margin="dense" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} sx={{ mt: 2 }} />
                  <TextField label="Confirm Password" type="password" fullWidth margin="dense" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} sx={{ mt: 2 }} />
                </DialogContent>
                <DialogActions sx={{ pb: 3, px: 3 }}>
                  <Button onClick={handlePasswordEditClose}>Cancel</Button>
                  <Button variant="contained" onClick={handlePasswordSave}>Save</Button>
                </DialogActions>
              </Dialog>

              {/* Personal Info Modal */}
              <Dialog open={isPersonalInfoEditOpen} onClose={handlePersonalInfoEditClose} fullWidth maxWidth="sm">
                <DialogTitle sx={{ pt: 4 }}>Edit Personal Info</DialogTitle>
                <DialogContent>
                  <TextField label="First Name" fullWidth margin="dense" value={firstName} onChange={(e) => setFirstName(e.target.value)} sx={{ mt: 2 }} />
                  <TextField label="Last Name" fullWidth margin="dense" value={lastName} onChange={(e) => setLastName(e.target.value)} sx={{ mt: 2 }} />
                  <TextField label="Date of Birth" fullWidth margin="dense" value={dateOfBirth} onChange={(e) => setDateOfBirth(e.target.value)} sx={{ mt: 2 }} />
                  
                  {/* Gender Dropdown */}
                  <FormControl fullWidth margin="dense">
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
                  <TextField label="Country of Residence" fullWidth margin="dense" value={country} onChange={(e) => setCountry(e.target.value)} sx={{ mt: 2 }} />
                  <TextField label="Education" fullWidth margin="dense" value={education} onChange={(e) => setEducation(e.target.value)} sx={{ mt: 2 }} />
                  <TextField label="Background Info" fullWidth multiline rows={3} margin="dense" value={backgroundInfo} onChange={(e) => setBackgroundInfo(e.target.value)} sx={{ mt: 2 }} />
                </DialogContent>
                <DialogActions sx={{ pb: 3, px: 3 }}>
                  <Button onClick={handlePersonalInfoEditClose}>Cancel</Button>
                  <Button variant="contained" onClick={handlePersonalInfoSave}>Save</Button>
                </DialogActions>
              </Dialog>

              {/* Language Edit Modal */}
              <Dialog open={isLanguageEditOpen} onClose={handleLanguageEditClose} fullWidth maxWidth="sm">
                <DialogTitle sx={{ pt: 4 }}>Edit Proficiency</DialogTitle>
                <DialogContent>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                    {selectedLanguage}
                  </Typography>
                  <TextField
                    select
                    fullWidth
                    margin="dense"
                    value={newProficiency || ""}
                    onChange={(e) => setNewProficiency(e.target.value)}
                    sx={{ mt: 2 }}
                  >
                    {Object.entries(proficiencyOptions).map(([value, label]) => (
                      <MenuItem key={value} value={value}>
                        {label}
                      </MenuItem>
                    ))}
                  </TextField>
                </DialogContent>
                <DialogActions sx={{ pb: 3, px: 3 }}>
                  <Button onClick={handleLanguageEditClose}>Cancel</Button>
                  <Button variant="contained" onClick={handleLanguageSave}>Save</Button>
                </DialogActions>
              </Dialog>
            </>
          )}
        </Box>
      </Container>
    </RoleCheck>
  );
}
