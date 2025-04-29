import Navbar_Listener from "components/nav_bar_listener";
import RoleCheck from "components/role_checker";
import styles from "stylesheets/listener_clip_list.module.css"

export default function ClipList() {
    return (
        // home page for listeners
        <RoleCheck requiredRole="listener">
            <Navbar_Listener/>
            <div className={styles.container}>
                <button className={styles.startButton}>
                        Start Audio Review
                </button>
            </div>
        </RoleCheck>
    );
}