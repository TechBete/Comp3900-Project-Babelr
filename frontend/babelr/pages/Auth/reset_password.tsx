import {useRouter } from "next/router";
import styles from "stylesheets/reset_password.module.css";
import { FormEvent, useState } from "react";

export default function ResetConfirmEmail() {
    const router = useRouter()
    const [error, setError] = useState("")

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        const formData = new FormData(event.currentTarget);
        const email = formData.get("email")
        try{
			const response = await fetch('http://localhost:8016/auth/blindEmailParse', {
				method:"POST",
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify({email}), 
			})

			if (response.ok) {
                const data = await response.json();

                if (data.listener_id) {
                    localStorage.setItem("id", data.listener_id);
                } else if (data.researcher_id) {
                    localStorage.setItem("id", data.researcher_id);
                }

				router.push("/Auth/reset_confirm"); // login for now change to verification later
			} else {
				const error = await response.json();
                setError(error)

			}
		} catch {
			setError("Network Error: Fetch Request Failed")
    	}
        
    }

    return (
        <div className={styles["reset-password-body"]}>
            <div className={styles["reset-password-container"]}>
                <h3 className={styles["reset-password-header"]}>Reset Your Password</h3>
                <p className={styles["reset-password-info"]}>Enter your email address and we will send you instructions to reset your password</p>
                <form className={styles["reset-password-form"]} method="post" onSubmit={handleSubmit}>
                    <div className={styles["reset-password-form-group"]}>
                        <label htmlFor="email">Email</label>
                        <input type="email" id="email" name="email" required />
                    </div>
                    <button type="submit" className={styles["reset-password-button"]}>Send Reset Instructions</button>
                </form>
                <p className={styles["back-to-login-link"]}><a href="/">Back to Login</a></p>
            </div>
        </div>
        


    );
} 