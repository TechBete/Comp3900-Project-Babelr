import Image from "next/image";
import Link from "next/link";
import { FormEvent, useState } from "react";
import styles from "stylesheets/login.module.css";
import { useRouter } from 'next/router'

export default function Login() {
    const router = useRouter()
    const [selectedOption, setSelectedOption] = useState("/Auth/register_listener");
    const [loginError, setLoginError] = useState("");

    // submission function to submit login details
    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
    
        const formData = new FormData(event.currentTarget);
        const email = formData.get("email")
        const pw = formData.get("password")

        try {
            // Login api call. 
            // input: {email: string, pw: string}
            // output: response
            const response = await fetch('http://localhost:8016/auth/login', {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, pw}),
                credentials: 'include'
            })


            // GetRole API call
            // input: nothing but notably requires credentials which is how it role checks
            if (response.ok) {
                const roleRes = await fetch("http://localhost:8016/auth/getRoleFromID", {
                    method: "GET",
                    credentials: "include",
                });

                const roleData = await roleRes.json();
                const role = roleData.role;
                const first_time = roleData.first_time;

                // if an invalid role returns an error
                if (!role) {
                    setLoginError("Unknown role");
                    return;
                }

                // if researcher pushes to the researcher pages
                if (role == "researcher") {
                    if (first_time){
                        router.push("/Researcher/first_time_researcher");
                    } else {
                        router.push("/Researcher/project_list");
                    }
                // else if listener pushes to listener pages
                } else if (role == "listener") {
                    if (first_time){
                        router.push("/Listener/first_time_listener");
                    } else {
                        router.push("/Listener/home_listener");
                    }
                // Another invalid role check for security
                } else {
                    setLoginError("Unknown type of user");
                }
            } else {
                const error = await response.json();
				setLoginError(error.error);
            }

        } catch {
            setLoginError("Network Error: Fetch Request Failed");
        }
    }

    // Rerouting to either user or register registration
    function handleUserChange(event: React.ChangeEvent<HTMLSelectElement>) {
        setSelectedOption(event.target.value);
    }


    return (    
        <div className={styles["login-body"]}>
            <div className={styles["login-container"]}>
                <Image className={styles["babelr-icon"]} src="/babelr_icon.png" alt="icon" width={100} height={100} />

                <h2 className={styles["login-header"]}>Babelr Login</h2>

                <form className={styles["login-form"]} method="post" onSubmit={handleSubmit}>
                    <div className={styles["login-form-details"]}>
                        <label htmlFor="email">Email</label>
                        <input type="email" id="email" name="email" required />
                    </div>

                    <div className={styles["login-form-details"]}>
                        <label htmlFor="password">Password</label> <span><Link href={"/Auth/reset_password"}>Forgot your Password?</Link></span>
                        <input type="password" id="password" name="password" required />
                    </div>

                    <button type="submit" className={styles["login-button"]}>
                        Login
                    </button>
                </form>

                <div className={styles["signup-link"]}>
                    Don&apos;t have an account? <Link href={selectedOption}>Sign up</Link>
                        <div>
                            <select name="Sign up as" value={selectedOption} onChange={handleUserChange}>
                                <option value={"/Auth/register_listener"}>User</option>
                                <option value={"/Auth/register_researcher"}>Researcher</option>
                            </select>
                        </div>
                </div>
                <div className={"error-label"}>
					{ loginError !== "" && <div>{loginError}</div>}
				</div>
            </div>
        </div>
    );
}