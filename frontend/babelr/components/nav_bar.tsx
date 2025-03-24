import styles from "../stylesheets/nav_bar.module.css"
import HomeIcon from "../components/homeicon"
import Link from "next/link"

export default function Navbar() {
    return ( 
        <div className={styles["nav-bar"]}>
            <HomeIcon/>
            <div className={styles["top-nav-right"]}>

                <div className={styles["profile-options"]}>
                    <span>My Profile</span>
                    <span><Link href='/'>Logout</Link></span>
                </div>
            </div>
        </div>
    )
} 