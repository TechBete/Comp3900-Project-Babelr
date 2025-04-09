import Navbar_Listener from "components/nav_bar_listener";
import RoleCheck from "components/role_checker";

export default function ClipList() {
    return (
        <RoleCheck requiredRole="listener">
            <Navbar_Listener/>
            <div style={{display: 'flex', justifyContent: 'center' , alignItems: 'center', height: '100vh', fontWeight: 'bold'}}>
                <button 
                    style={{
                        padding: '12px 24px',
                        fontSize: '1.1rem',
                        fontWeight: 'bold',
                        backgroundColor: '#1976d2',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Start Audio Review
                </button>
            </div>
        </RoleCheck>
    );
}