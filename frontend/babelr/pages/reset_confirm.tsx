import styles from "../stylesheets/reset_confirm.module.css";

export default function ResetConfirmEmail() {
    return (
        <div className={styles["reset-body"]}>
            <div className={styles["reset-container"]}>
                <h2 className={styles["reset-header"]}>Enter a new password</h2>
                <form className={styles["reset-form"]}>
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