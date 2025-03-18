import styles from "../stylesheets/nav_bar.module.css"
import HomeIcon from "../components/homeicon"

export default function Navbar() {
    return ( 
        <div className={styles["nav-bar"]}>
            <HomeIcon/>
            <div className={styles["top-nav-right"]}>
                <div className={styles["search-bar"]}>
                    <input type="text" placeholder="Search" />
                </div>
                <div className={styles["profile-options"]}>
                    <span>My Profile</span>
                    <span>Logout</span>
                </div>
            </div>
        </div>
    )
} 