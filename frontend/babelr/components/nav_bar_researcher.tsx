import styles from "../stylesheets/nav_bar.module.css"
import HomeIcon from "./homeicon"
import Link from "next/link"

export default function Navbar() {
    return ( 
        <div className={styles["nav-bar"]}>
            <Link href='/Researcher/project_list'><HomeIcon/></Link>
            <div className={styles["top-nav-right"]}>

                <div className={styles["profile-options"]}>
                    <span><Link href='/Researcher/profile'>My Profile</Link></span>
                    <span><Link href='/'>Logout</Link></span>
                </div>
            </div>
        </div>
    )
} 