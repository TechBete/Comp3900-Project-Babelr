import RoleCheck from "components/role_checker";
import Navbar from "components/nav_bar_researcher";
import Sidebar from "components/project_sidebar";
import { useRouter } from 'next/router';
import Box from '@mui/material/Box';


// testing analytics
import { BarChart } from '@mui/x-charts/BarChart';

function getDataset() {
    return [
        {name: 'Mean', ModelA: 42, ModelB: 3.2, ModelC: 5.1,}
    ];
}

function valueFormatter(value: number | null) {
    return `${value}`;
}

export default function Analytics() {
    const { projectName } = useRouter().query;
    if (typeof projectName !== 'string') {
        return <div>Loading?</div>;
    }


    return (
        <RoleCheck requiredRole="researcher">
            <Navbar/>
            <Box sx={{ display: 'flex' }}>
                <Sidebar project_name={projectName} />

                <Box
                    component="main"
                    sx={{
                        flexGrow: 1,
                        mt: '50px',  // navbar height
                        p: 3,
                        height: 'calc(100vh - 50px)',
                        overflow: 'auto',
                        backgroundColor: '#f5f5f5',
                    }}
                >
                    
                    <h1>Analytics</h1>
                    <Box
                    sx={{
                        height: 'calc(80vh - 50px)'
                    }}>
                    <BarChart
                        dataset={getDataset()}
                        xAxis={[{ scaleType: 'band', dataKey: 'name' }]}
                        series={[
                            {dataKey: 'ModelA', label: 'Model A', valueFormatter},
                            {dataKey: 'ModelB', label: 'Model B', valueFormatter},
                            {dataKey: 'ModelC', label: 'Model C', valueFormatter},
                        ]}
                        // height={300}
                    />
                    </Box>
                </Box>
            </Box>
        </RoleCheck>
    );
}