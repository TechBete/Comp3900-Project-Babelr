import styles from "stylesheets/first_time_listener.module.css"
import Image from "next/image";
import { FormEvent, useState } from "react";
import RoleCheck from "components/role_checker";
import router from "next/router";

export default function First_time() {
    const [Error, setError] = useState("");

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        const formData = new FormData(event.currentTarget);
        console.log(Object.fromEntries(formData.entries()));

        PostDemographics(formData)
        console.log(Error)
    }

    async function PostDemographics(formData: FormData) {
        console.log("DEMOGRAPHICS POST BELOW");
        console.log("after", JSON.stringify(Object.fromEntries(formData)));
        router.push('project_list')
        try {
            const response = await fetch(`http://localhost:8016/researcher/updateFirstTime`, {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(Object.fromEntries(formData)),
                credentials: 'include'
            })
    
            if (response.ok) {
                // const response = await response.json()
                router.push('project_list')
            } else {
                const error = await response.json();
                setError(error.error);
            }
    
        } catch {
            setError("Network Error: Fetch Request Failed");
        }        
    }


    return (
        <RoleCheck requiredRole="researcher">
            <div className={styles["body"]}>
                <div className={styles["form-container"]}>
                    <div className={styles["information-container"]}>
                        <div className={styles["header-wrapper"]}>
                            <h1>Welcome to Babelr</h1>
                            <p>Please fill in the information below</p>
                            <form className={styles["demographics-forms"]} method="post" onSubmit={handleSubmit}>
                                <label htmlFor="first_name">First Name</label>
                                <input 
                                    className={styles.input}
                                    type="text" 
                                    id="first_name" 
                                    name="first_name" 
                                required
                                />

                                <label htmlFor="last_name">Last Name</label>
                                <input 
                                    className={styles.input}
                                    type="text" 
                                    id="last_name" 
                                    name="last_name" 
                                    required
                                />
                                
                                <label htmlFor="organisation">Organisation</label> 
                                <select 
                                    className={styles.select} 
                                    id="organisation" 
                                    name="organisation" 
                                    required
                                >       
                                    <option value="" disabled >Select Your Organisation</option>
                                    <option>UNSW</option>
                                    <option>USYD</option>
                                    <option>CSIRO</option>
                                </select>

                                <button className={styles.button}type="submit">Next</button>
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