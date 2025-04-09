// import styles from "../stylesheets/nav_bar.module.css"
// import HomeIcon from "./homeicon"
// import Link from "next/link"

// export default function Navbar() {
//     return ( 
//         <div className={styles["nav-bar"]}>
//             <Link href='/Listener/clip_list'><HomeIcon/></Link>
//             <div className={styles["top-nav-right"]}>

//                 <div className={styles["profile-options"]}>
//                     <span>Points</span>
//                     <span><Link href='/Listener/profile'>My Profile</Link></span>
//                     <span><Link href='/'>Logout</Link></span>
//                 </div>
//             </div>
//         </div>
//     )
// } 

import { useEffect, useState } from "react";
import styles from "../stylesheets/nav_bar.module.css";
import HomeIcon from "./homeicon";
import Link from "next/link";

export default function Navbar() {
    const [points, setPoints] = useState(null);

    useEffect(() => {
        const fetchPoints = async () => {
            try {
                const res = await fetch("http://localhost:8016/listener/getCurrentPoints", {
                    method: "GET",
                    credentials: "include",  // important for cookie-based JWTs
                });

                if (!res.ok) {
                    throw new Error("Failed to fetch points");
                }

                const data = await res.json();
                setPoints(data.reward_points);
            } catch (error) {
                console.error("Error fetching points:", error);
            }
        };

        fetchPoints();
    }, []);

    return ( 
        <div className={styles["nav-bar"]}>
            <Link href='/Listener/clip_list'><HomeIcon/></Link>
            <div className={styles["top-nav-right"]}>
                <div className={styles["profile-options"]}>
                    <span>Points: {points !== null ? points : "..."}</span>
                    <span><Link href='/Listener/profile'>My Profile</Link></span>
                    <span><Link href='/'>Logout</Link></span>
                </div>
            </div>
        </div>
    );
}
