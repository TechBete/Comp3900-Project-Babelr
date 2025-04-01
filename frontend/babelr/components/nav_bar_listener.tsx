import { useState } from "react";
import styles from "../stylesheets/nav_bar.module.css"
import HomeIcon from "../components/homeicon"
import Link from "next/link"

export default function Navbar_Listener() {
    const [Error, setError] = useState("");
    const [Points, setPoints] = useState(0);

    async function getPoints() {
        console.log("DEMOGRAPHICS POST BELOW");
        console.log(JSON.stringify({}));
        try {
            const response = await fetch(`http://localhost:8016/getPoints}`, {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({}),
                credentials: 'include'
            })
    
            if (response.ok) {
                // const response = await response.json()
                console.log(response);
                setPoints(0);
                return // change later maybe
            } else {
                const error = await response.json();
                setError(error.error);
            }
    
        } catch {
            // setError("Network Error: Fetch Request Failed");
        }
    }


    return ( 
        <div className={styles["nav-bar"]}>
            <HomeIcon/>
            <div className={styles["top-nav-right"]}>

                <div className={styles["profile-options"]}>
                    <span><Link href='/rewards_system'>Points: {getPoints()}</Link></span>
                    <span>My Profile</span>
                    <span><Link href='/'>Logout</Link></span>
                </div>
            </div>
        </div>
    )
}