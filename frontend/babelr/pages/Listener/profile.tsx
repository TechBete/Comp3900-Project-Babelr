import RoleCheck from "components/role_checker";
import Link from "next/link";
import Navbar from "components/nav_bar_listener";

export default function ClipList() {
    return (
        <RoleCheck requiredRole="listener">
            <Navbar/>
            <div style={{display: 'flex', justifyContent: 'center' , alignItems: 'center', height: '100vh', fontWeight: 'bold'}}>
                THIS IS A TEMP LISTENER PROFILE PAGE TO TEST ROUTING.
                <Link style={{textDecoration: 'underline', color: 'blue'}}href='/Listener/clip_list'>Back to Home</Link>
            </div>
        </RoleCheck>
    );
}