
import { useState, useEffect } from "react";
import styles from "../stylesheets/nav_bar.module.css"
import HomeIcon from "../components/homeicon"
import Link from "next/link"

export default function Navbar_Listener() {
    const [Error, setError] = useState("");
    const [Points, setPoints] = useState(0);

    useEffect(() => {
        getCurrentPoints();
    });

    async function getCurrentPoints() {
        console.log("Return prev points");
        console.log(Points);
        try {
            const response = await fetch(`http://localhost:8016/getCurrentPoints`, {
                method:"GET",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({}),
                credentials: 'include'
            })
    
            if (response.ok) {
                console.log("reached?")
                const res = await response.json()
                console.log(res);
                console.log(res.reward_points);
                setPoints(res.reward_points);
                return // change later maybe
            } else {
                console.log("iss issue?");
                const error = await response.json();
                setError(error.error);
            }
    
        } catch {
            console.log("an error occured in call to getCurrentPoints");
            // setError("Network Error: Fetch Request Failed");
            return Error;
        }
    }

    return ( 
        <div className={styles["nav-bar"]}>
            <Link href='/Listener/clip_list'><HomeIcon/></Link>
            <div className={styles["top-nav-right"]}>
                <div className={styles["profile-options"]}>
                    <span><Link href='/Listener/rewards_shop'>Points: {Points}</Link></span>
                    <span><Link href='/Listener/profile'>My Profile</Link></span>
                    <span><Link href='/'>Logout</Link></span>
                </div>
            </div>
        </div>
    )
}
