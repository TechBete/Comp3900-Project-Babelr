import RoleCheck from "components/role_checker";
import Link from "next/link";

export default function ClipList() {
    return (
        <RoleCheck requiredRole="listener">
            <div style={{display: 'flex', justifyContent: 'center' , alignItems: 'center', height: '100vh', fontWeight: 'bold'}}>
                THIS IS A TEMP RESEARCHER PROFILE PAGE TO TEST ROUTING.
                <Link style={{textDecoration: 'underline', color: 'blue'}}href='/Researcher/project_list'>Back to Home</Link>
            </div>
        </RoleCheck>
    );
}