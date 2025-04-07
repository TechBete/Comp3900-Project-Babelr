import { FormEvent, useState } from "react";
import styles from "stylesheets/first_time_listener.module.css";
import Image from "next/image";
import DatePickerWrapper from "components/date_picker"
import { useRouter } from "next/router";
import RoleCheck from "components/role_checker";

export default function First_time() {
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [gender, setGender] = useState("");
    const [country, setCountry] = useState("");
    const [education, setEducation] = useState("");
    const [Error, setError] = useState("");
    const router = useRouter();

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        const formData = new FormData(event.currentTarget);
        // formData.set("age", String(getAge(new Date(formData.get("dob") as string))));
        console.log("hello", Object.fromEntries(formData.entries()));

        PostDemographics(formData)
        console.log(Error)
    }

    async function PostDemographics(formData: FormData) {
        console.log("DEMOGRAPHICS POST BELOW");
        console.log("after", JSON.stringify(Object.fromEntries(formData)));
        try {
            const response = await fetch(`http://localhost:8016/auth/registerListenerDemographics`, {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(Object.fromEntries(formData)),
                credentials: 'include'
            })
    
            if (response.ok) {
                // const response = await response.json()
                router.push('first_time_listener_lg')
            } else {
                const error = await response.json();
                setError(error.error);
            }
    
        } catch {
            setError("Network Error: Fetch Request Failed");
        }
    }


    return (
        <RoleCheck requiredRole="listener">
            <div className={styles["body"]}>
                <div className={styles["form-container"]}>
                    <div className={styles["information-container"]}>
                        <div className={styles["header-wrapper"]}>
                            <h1>Welcome to Babelr</h1>
                            <p>Please fill in the information below</p>
                            <form className={styles["demographics-forms"]} method="post" onSubmit={handleSubmit}>

                                <label className={styles.label} htmlFor="first_name">First Name</label>
                                <input 
                                    className={styles.input} 
                                    type="text" 
                                    id="first_name" 
                                    name="first_name" 
                                    value={firstName}
                                    onChange={(e) => setFirstName(e.target.value)}
                                    required
                                />
        
                                <label className={styles.label} htmlFor="last_name">Last Name</label>
                                <input 
                                    className={styles.input} 
                                    type="text" 
                                    id="last_name" 
                                    name="last_name" 
                                    value={lastName}
                                    onChange={(e) => setLastName(e.target.value)}
                                    required
                                />
        
                                {/* <label className={styles.label} htmlFor="phone">Phone Number</label>
                                <input className={styles.input} type="text" id="phone" name="phone" required/> */}
        
                                <label className={styles.label} htmlFor="gender">Gender</label>
                                <select 
                                    className={styles.select} 
                                    id="gender" 
                                    name="gender" 
                                    value={gender} 
                                    onChange={(e) => setGender(e.target.value)}
                                    required
                                >
                                    <option value="" disabled>Select Your Gender</option>
                                    <option>Male</option>
                                    <option>Female</option>
                                    <option>Other</option>
                                </select>
        
                                <label className={styles.label} htmlFor="date_of_birth">Date of Birth</label>
                                <DatePickerWrapper/>
                                
                                <label className={styles.label} htmlFor="country_of_residence">Country of Residence</label> 
                                <select 
                                    className={styles.select}
                                    id="country_of_residence" 
                                    name="country_of_residence" 
                                    value={country} 
                                    onChange={(e) => setCountry(e.target.value)}
                                    required
                                >       
                                    <option value="" disabled selected>Select Your Country of Residence</option> 
                                    <option>Australia</option>
                                    <option>USA</option>
                                    <option>UK</option>
                                    <option>Canada</option>
                                </select>
        
        
        
                                <label className={styles.label} htmlFor="education">What is your highest level of completed education?</label>
                                <select 
                                    className={styles.select} 
                                    id="education" 
                                    name="education" 
                                    value={education} 
                                    onChange={(e) => setEducation(e.target.value)}
                                    required
                                    >
                                    <option value="" disabled selected>Select Your Education Level</option> 
                                    <option>University</option>
                                    <option>High School</option>
                                    <option>Elementary</option>
                                    <option>None</option>
                                </select>
        
                                <button className={styles.button} type="submit">Next</button>
                                <div className="error-label">
                                    { Error !== "" && <div>{Error}</div>}
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
                <div className={styles["image-container"]}>
                    <Image src="/babelr_logo.png" alt="side-image" width={1024} height={1024}/>
                </div>
            </div>
        </RoleCheck>
    );
}   