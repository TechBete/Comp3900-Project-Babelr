import styles from "../stylesheets/nav_bar.module.css"
import HomeIcon from "./homeicon"
import Link from "next/link"
import Points from "components/points"

export default function Navbar() {
    return ( 
        <div className={styles["nav-bar"]}>
            <Link href='/Listener/clip_list'><HomeIcon/></Link>
            <div className={styles["top-nav-right"]}>

                <div className={styles["profile-options"]}>
                    <span><Points/></span>
                    <span><Link href='/Listener/profile'>My Profile</Link></span>
                    <span><Link href='/'>Logout</Link></span>
                </div>
            </div>
        </div>
    )
} 