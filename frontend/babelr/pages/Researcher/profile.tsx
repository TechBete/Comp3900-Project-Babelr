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
        console.error("Failed to fetch researcher data.");
      }
    } catch (err) {
      console.error("Fetch error:", err);
    }
  }

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
              {/* Debugging: Show entire researcher data */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Full Researcher Data (Debugging)</Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="body2">{JSON.stringify(researcherData, null, 2)}</Typography>
                </CardContent>
              </Card>

              {/* User Details */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>User Details</Typography>
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
                  <Typography variant="h6" gutterBottom>Personal Info</Typography>
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
                      <ListItemText primary="Gender" secondary={researcherData["Gender"] || "Not specified"} />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="Country" secondary={researcherData["Country"]} />
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
        </Box>
      </Container>
    </RoleCheck>
  );
}
