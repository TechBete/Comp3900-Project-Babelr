import router from "next/router";
import styles from "stylesheets/reset_confirm.module.css";
import { FormEvent, useState } from "react";

export default function ResetConfirmEmail() {
    const [error, setError] = useState("")

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
            event.preventDefault()
    
            const formData = new FormData(event.currentTarget);
            const id = localStorage.getItem('id');
            const pw = formData.get("new-password");
            const confirmPw = formData.get("confirm-password");
            try{
                // Reset Password API call Note: does not require email verification just an email that is registered in the system
                const response = await fetch('http://localhost:8016/auth/blindPasswordReset', {
                    method:"POST",
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({"pw": pw, "pw_confirmation": confirmPw, "id": id}), 
                })
    
                if (response.ok) {
                    router.push("/Auth/login");  // Reroute to login on successful reset
                } else {
                    const e = await response.json();
                    setError(e);
                }
    
                const formJson = Object.fromEntries(formData.entries());
            } catch {
                setError("Network Error");
            }
            
        }

    return (
        <div className={styles["reset-body"]}>
            <div className={styles["reset-container"]}>
                <h2 className={styles["reset-header"]}>Enter a new password</h2>
                <form className={styles["reset-form"]} method="post" onSubmit={handleSubmit}>
                    <div className={styles["reset-form-group"]}>
                        <label htmlFor="new-password">New Password</label>
                        <input type="password" id="new-password" name="new-password" required />
                    </div>
                    <div className={styles["reset-form-group"]}>
                        <label htmlFor="confirm-password">Confirm Password</label>
                        <input type="password" id="confirm-password" name="confirm-password" required />
                    </div>
                    <button type="submit" className={styles["reset-button"]}>Update Password</button>
                </form>
            </div>
        </div>
    );
}