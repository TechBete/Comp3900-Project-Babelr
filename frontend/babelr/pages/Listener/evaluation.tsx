import styles from "stylesheets/first_time_listener.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import { useState, useEffect } from "react";
// import { Button } from "@mui/material";

export default function Evaluation() {
    const [Error, setError] = useState("");

    useEffect(() => {
        Audio_Receiver();
    });

    async function submitRating() {
        console.log("Submit rating was hit!!!")
        try {
            const response = await fetch(`http://localhost:8016/submitRating}`, {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({"id": 2}),
                credentials: 'include'
            })
    
            if (response.ok) {
                console.log("HAHAHAHAHHAHAHAHHA!!!");
                // const response = await response.json()
                return // change later maybe
            } else {
                console.log("Banana Apple Berry Cherry Merry!!!");
                const error = await response.json();
                setError(error.error);
            }
    
        } catch {
            console.log("There was a network error unforunate/1111");
            setError("Network Error: Fetch Request Failed");
            return Error;
        }
    }

    async function Audio_Receiver() {
        try {
            const response = await fetch(`http://localhost:8016/audioAllocate}`, {
                method:"GET",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({}),
                credentials: 'include'
            })
    
            if (response.ok) {

                // const response = await response.json()
                return // change later maybe
            } else {
                const error = await response.json();
                setError(error.error);
            }
    
        } catch {
            setError("Network Error: Fetch Request Failed");
            return Error;
        }
    }

    return (
        <div>
            <Navbar_Listener></Navbar_Listener>
            <div className={styles["body"]}>
                <div className={styles["form-container"]}>
                    <div className={styles["information-container"]}>
                        <div className={styles["header-wrapper"]}>
                            <h1>Evaluation</h1>
                            <p>Please start your evaluation below.</p>
                            <form className={styles["login-form"]} method="post" onSubmit={submitRating}>
                                {/*<Button variant="contained" type='submit'>Submit Rating</Button>*/}
                                <button type="submit">Next</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}