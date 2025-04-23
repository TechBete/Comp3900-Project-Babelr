import styles from "stylesheets/home_listener.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import Link from "next/link";
import RoleCheck from "components/role_checker";

export default function Home_Listener() {
    return (
        <RoleCheck requiredRole="listener">
            <div>
                <Navbar_Listener></Navbar_Listener>
                <div className={styles["body"]}>
                    <div className={styles["container"]}>
                        <h2 className={styles["header"]}>User Register</h2>
                        <p>Click the Start Rating button to begin.</p>
                        <p className={styles["button"]}>
                            <Link href="/Listener/evaluation">Start Rating</Link>
                        </p>
                    </div>
                </div>
            </div>
        </RoleCheck>
    );
}
