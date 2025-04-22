import { useEffect, useState } from "react";

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
        setResearcherData(data);
      } else {
        console.error("Failed to fetch researcher data.");
      }
    } catch (err) {
      console.error("Fetch error:", err);
    }
  }

  return (
    <div>
      <h1>Researcher Profile</h1>
      <pre>{JSON.stringify(researcherData, null, 2)}</pre>
    </div>
  );
}
