import Image from "next/image";
import Link from "next/link";
import { FormEvent, useState } from "react";
import styles from "stylesheets/login.module.css";
import { useRouter } from 'next/router'

export default function Login() {
    const router = useRouter()
    const [selectedOption, setSelectedOption] = useState("/Auth/register_listener");
    const [loginError, setLoginError] = useState("");
    // FOR NOW USE THIS TO CHANGE WHAT THE USERTYPE IS AND IF IT'S THEIR FIRST TIME
    const [isFirstTime, setFirstTime] = useState(true); // temporary before isfirstime call
    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        // DOES NOTHING BECAUSE ASYNC FUNCTION BUT JUST TO KEEP COMPILER HAPPY
        setFirstTime(true);

        event.preventDefault()
    
        const formData = new FormData(event.currentTarget);
        const email = formData.get("email")
        const pw = formData.get("password")

        try {
            const response = await fetch('http://localhost:8016/auth/login', {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, pw}),
                credentials: 'include'
            })

            if (response.ok) {
                const roleRes = await fetch("http://localhost:8016/getRoleFromID", {
                    method: "GET",
                    credentials: "include",
                });

                const roleData = await roleRes.json();
                const role = roleData.role;
                if (!role) {
                    setLoginError("Unknown role");
                    return;
                }
                console.log("going here?");

                if (role == "researcher") {
                    if (isFirstTime){
                        console.log("going here???");
                        router.push("/Researcher/first_time_researcher");
                    } else {
                        router.push("/Researcher/project_list");
                    }
                } else if (role == "listener") {
                    if (isFirstTime){
                        console.log("going here");
                        router.push("/Listener/first_time_listener");
                    } else {
                        console.log("going here?????????");
                        router.push("/Listener/clip_list");
                    }
                } else {
                    setLoginError("Unknown type of user");
                }
            } else {
                const error = await response.json();
                console.log(error.error);
				setLoginError(error.error);
            }

        } catch {
            setLoginError("Network Error: Fetch Request Failed");
        }
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
                        <input type="email" id="email" name="email" required />
                    </div>

                    <div className={styles["login-form-details"]}>
                        <label htmlFor="pw">Password</label> <span><Link href={"/Auth/reset_password"}>Forgot your Password?</Link></span>
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