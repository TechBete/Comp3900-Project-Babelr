import router from "next/router";
import styles from "stylesheets/reset_confirm.module.css";
import { FormEvent } from "react";

export default function ResetConfirmEmail() {

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
            event.preventDefault()
    
            const formData = new FormData(event.currentTarget);
            const id = localStorage.getItem('id');
            const pw = formData.get("new-password");
            const confirmPw = formData.get("confirm-password");
            try{
                const response = await fetch('http://localhost:8016/blindPasswordReset', {
                    method:"POST",
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({"pw": pw, "pw_confirmation": confirmPw, "id": id}), 
                })
    
                if (response.ok) {
                    console.log(JSON.stringify({"pw": pw, "pw_confirmation": confirmPw, "id": id}));
                    router.push("/Auth/login"); // login for now change to verification later
                } else {
                    const error = await response.json();
                    console.log(error.error);
                    console.log(JSON.stringify({"pw": pw, "pw_confirmation": confirmPw, "id": id}))
                }
    
                const formJson = Object.fromEntries(formData.entries());
                console.log(formJson);
            } catch {
                console.log("Network Error: Fetch Request Failed")
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