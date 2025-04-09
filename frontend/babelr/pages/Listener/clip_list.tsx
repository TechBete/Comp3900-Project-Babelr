import Navbar_Listener from "components/nav_bar_listener";
import RoleCheck from "components/role_checker";

export default function ClipList() {
    return (
        <RoleCheck requiredRole="listener">
            <Navbar_Listener/>
            <div style={{display: 'flex', justifyContent: 'center' , alignItems: 'center', height: '100vh', fontWeight: 'bold'}}>
                THIS IS A TEMP CLIP LIST PAGE TO TEST ROUTING.
            </div>
        </RoleCheck>
    );
}