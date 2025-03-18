import Image from "next/image";
import Link from "next/link";
import { FormEvent, useState } from "react";
import styles from "../stylesheets/login.module.css";
import { useRouter } from "next/router";



export default function RegisterListener() {
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [equalPassError, setEqualPassError] = useState(false);
	const [emailError, setEmailError] = useState(false);
	const [registerError, setRegisterError] = useState("");
	const router = useRouter();


	function handleConfirmBlur() {
		if (confirmPassword && password != "") {
			setEqualPassError(password !== confirmPassword);
		}
	}
  

	async function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault()
		const formData = new FormData(event.currentTarget);
		const email = formData.get("email")
		const pw = formData.get("pw") 

		const formJson = Object.fromEntries(formData.entries());
		console.log(formJson);

		if (emailError || equalPassError) {
		return;
		}

		try{
			const response = await fetch('http://127.0.0.1:8016/registerListener', {
				method:"POST",
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify({        
					email,
					pw,
					first_name: "temp_fn",
					last_name: "temp_ln"}), //following /registerListener format 
			})

			if (response.ok) {
				router.push("/login"); // login for now change to verification later
				setRegisterError("");
			} else {
				const error = await response.json();
				console.log(error.error);
				setRegisterError(error.error);
			}

			const formJson = Object.fromEntries(formData.entries());
			console.log(formJson);
		} catch {
			setRegisterError("Network Error: Fetch Request Failed")
    	}
	}


	return (    
		<div className={styles["login-body"]}>
			<div className={styles["login-container"]}>
				<Image className={styles["babelr-icon"]} src="/babelr_icon.png" alt="icon" width={100} height={100} />
				
				<h2 className={styles["login-header"]}>User Register</h2>
				<form className={styles["login-form"]} method="post" onSubmit={handleSubmit}>
					<div className={styles["login-form-details"]}>
						<label htmlFor="email" className={emailError ? styles["invalid-label"] : ""}>
							{ emailError && <span>*</span> }Email
						</label>
						<input type="email" id="email" name="email" required onInvalid={() => setEmailError(true) } onInput={() => setEmailError(false)} />
							{emailError && <div className={styles["invalid-label"]}>Invalid email form</div>}
					</div>

					<div className={styles["login-form-details"]}>
						<label htmlFor="pw" className={equalPassError ? styles["invalid-label"] : ""}>
							{ equalPassError && <span style={{ color: "red" }}>*</span>}Password
						</label>
						<input type="password" id="pw" name="pw" required  value={password} onChange={(e) => setPassword(e.target.value)} onBlur={handleConfirmBlur}/>
					</div>

					<div className={styles["login-form-details"]}>
						<label htmlFor="confirmPw" className={equalPassError ? styles["invalid-label"] : ""}>
							{ equalPassError && <span>*</span> }Confirm Password
						</label>
					
					<input type="password" id="confirmPw" name="confirmPw" required  value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} onBlur={handleConfirmBlur}/>
						<div className={styles["invalid-label"]}>
							{ equalPassError && <div>Passwords don&apos;t match</div>}
						</div>
					</div>

					<div className={styles["invalid-label"]}>
						{ registerError !== "" && <div>{registerError}</div>}
					</div>
					<button type="submit" className={styles["login-button"]}>
						Register
					</button>
				</form>

				<p className={styles["signup-link"]}>
					Already have an account? <Link href="/login">Sign in</Link>
				</p>
			</div>
		</div>
  	);
}