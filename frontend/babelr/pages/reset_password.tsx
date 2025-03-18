import {useRouter } from "next/router";
import styles from "../stylesheets/reset_password.module.css";
import { FormEvent } from "react";

export default function ResetConfirmEmail() {
    const router = useRouter()

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        // const formData = new FormData(event.currentTarget);
        // const email = formData.get("email")
        // const response = fetch() send email fetch response etc

        const response = true; 
        if (response) {
            router.push('/reset_confirm');
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