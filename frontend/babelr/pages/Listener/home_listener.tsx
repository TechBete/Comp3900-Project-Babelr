import styles from "stylesheets/home_listener.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import Link from "next/link";

export default function Home_Listener() {
    return (
        <div>
            <Navbar_Listener></Navbar_Listener>
            <div className={styles["body"]}>
                <div className={styles["container"]}>
                    <h2 className={styles["header"]}>User Register</h2>
                    <p>Here are the instructions for how the rating process will work for a user.</p>
                    <p className={styles["button"]}>
                        <Link href="/Listener/evaluation">Start Rating</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
