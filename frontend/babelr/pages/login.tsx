import Image from "next/image";
import Link from "next/link";
import { FormEvent, useState } from "react";
import styles from "../stylesheets/login.module.css";
import { useRouter } from 'next/router'

export default function Login() {
    const router = useRouter()
    const [selectedOption, setSelectedOption] = useState("/register_listener");


    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
    
        const formData = new FormData(event.currentTarget);
        const email = formData.get("email")
        const password = formData.get("password")

        const response = await fetch('http://127.0.0.1:8016/login', {
            method:"POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password}),
        })

        if (response.ok) {
            router.push('/login')
          } else {
            console.log(response.json())
        }

        const formJson = Object.fromEntries(formData.entries());
        console.log(formJson);
    }

    function handleUserChange(event: React.ChangeEvent<HTMLSelectElement>) {
        setSelectedOption(event.target.value);
        console.log("Selected:", event.target.value);
    }
  

    return (    
        <div className={styles["login-body"]}>
            <div className={styles["login-container"]}>
                <Image className={styles["babelr-icon"]} src="/babelr_icon.png" alt="icon" width={100} height={100} />

                <h2 className={styles["login-header"]}>Babelr Login</h2>

                <form className={styles["login-form"]} method="post" onSubmit={handleSubmit}>
                    <div className={styles["login-form-details"]}>
                        <label htmlFor="email">Email</label>
                        <input type="email" id="email" name="username" required />
                    </div>

                    <div className={styles["login-form-details"]}>
                        <label htmlFor="password">Password</label> <span><Link href={"/reset_confirm"}>Forgot your Password?</Link></span>
                        <input type="password" id="password" name="password" required />
                    </div>

                    <button type="submit" className={styles["login-button"]}>
                        Login
                    </button>
                </form>

                <p className={styles["signup-link"]}>
                    Don&apos;t have an account? <Link href={selectedOption}>Sign up</Link>
                        <div>
                            <select name="Sign up as" value={selectedOption} onChange={handleUserChange}>
                                <option value={"/register_listener"}>User</option>
                                <option value={"/register_researcher"}>Researcher</option>
                            </select>
                        </div>
                </p>
            </div>
        </div>
    );
}

{/* <Link href="/register_listener">Sign up</Link> */}