import Image from "next/image";
import Link from "next/link";
import { FormEvent, useState } from "react";
import styles from "../stylesheets/login.module.css";

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        if (!checkEmail() || !checkPassword()) {

        }
        
        const form = event.target as HTMLFormElement;
        const formData = new FormData(form);

        // fetch('/')//backedn

        const formJson = Object.fromEntries(formData.entries());
        console.log(formJson);
    }
  

    return (
        <div className={styles["login-body"]}>
            <div className={styles["login-container"]}>
                <Image className={styles["babelr-icon"]} src="/babelr_icon.png" alt="icon" width={100} height={100} />
                
                <h2 className={styles["login-header"]}>Babelr Login</h2>

                <form className={styles["login-form"]} method="post" onSubmit={handleSubmit}>
                    <div className={styles["login-form-details"]}>
                        <label htmlFor="username">Email</label>
                        <input type="text" id="username" name="username" required />
                    </div>

                    <div className={styles["login-form-details"]}>
                        <label htmlFor="password">Password</label>
                        <input type="password" id="password" name="password" required />
                    </div>

                    <button type="submit" className={styles["login-button"]} onSubmit={() => handleSubmit(email, password)}>
                        Login
                    </button>
                </form>

                <p className={styles["signup-link"]}>
                    Don&apos;t have an account? <Link href="/signup">Sign up</Link>
                </p>
            </div>
        </div>
    );
}