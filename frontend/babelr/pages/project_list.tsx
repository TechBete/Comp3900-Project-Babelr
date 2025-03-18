import Link from "next/link";
import styles from "../stylesheets/projects_list.module.css"
import Navbar from "../components/nav_bar";
import Sidebar from "../components/side_bar";
import Modal from "../components/popout_modal";
import { FormEvent, useState } from "react";


// function Projects({}) {
//     return (
//     <tr className={styles["tr"]}>
//         <td className={styles["td"]}><Link className={styles["projects-link"]} href="/Project1">Project 1</Link></td>
//         <td className={styles["td"]}><span className={`${styles.status} ${styles["in-progress"]}`}>In Progress</span></td>
//         <td className={styles["td"]}>Dr Bryan</td>
//     </tr>
//     );
// }

export default function MainScreen() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [projectName, setProjectName] = useState("Project_4");
    const [createError, setCreateError] = useState("");

    async function handleCreate(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
		// const formData = new FormData(event.currentTarget);
        try {
            const response = await fetch('http://localhost:8016/createProject', {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({"project_name": projectName}),
                credentials: 'include'
            })
        
            if (response.ok) {
				console.log("OK");
                console.log(JSON.stringify({"project_name": projectName, "researcher_id": "1"}));
			} else {
                const error = await response.json()
                console.log(JSON.stringify({"project_name": projectName, "researcher_id": "1"}));
				console.log("NOT OK");
                console.log(error.error);
			}
        } catch {
            setCreateError("Network Error: Fetch Request Failed");
        }
    }

    return (
        <div className={styles["project-body"]}>
            < Navbar/>
            <div className={styles["container"]}>
                <Sidebar/>
                <div className={styles["main-content"]}>
                    <h2 className={styles["projects-h2"]}>Projects</h2>
                    <table className={styles["table"]}>
                        <thead className={styles["thead"]}>
                            <tr className={styles["tr"]}>
                                <th className={styles["th"]}>Name</th>
                                <th className={styles["th"]}>Status</th>
                                <th className={styles["th"]}>Creator</th>
                                <th className={styles["th"]}></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr className={styles["tr"]}>
                                <td className={styles["td"]}><Link className={styles["projects-link"]} href="/Project1">Project 1</Link></td>
                                <td className={styles["td"]}><span className={`${styles.status} ${styles["in-progress"]}`}>In Progress</span></td>
                                <td className={styles["td"]}>Dr Bryan</td>
                            </tr>
                            <tr className={styles["tr"]}>
                                <td className={styles["td"]}><Link className={styles["projects-link"]} href="/Project2">Project 2</Link></td>
                                <td className={styles["td"]}><span className={`${styles.status} ${styles["complete"]}`}>Complete</span></td>
                                <td className={styles["td"]}>Bill</td>
                            </tr>
                            <tr className={styles["tr"]}>
                                <td className={styles["td"]}><Link className={styles["projects-link"]} href="/Project3">Project 3</Link></td>
                                <td className={styles["td"]}><span className={`${styles.status} ${styles["draft"]}`}>Draft</span></td>
                                <td className={styles["td"]}>Bob</td>
                            </tr>
                        </tbody>
                    </table>

                    <button className={styles["add-project-btn"]} onClick={() => setIsModalOpen(true)}> + </button>
                    <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} hasCloseBtn>
                        <h2 className={styles.modalTitle}>New Project</h2>

                        <form onSubmit={handleCreate}>
                            <label htmlFor="project_name" className={styles.formLabel}>
                                Project Name
                            </label>
                            <input
                                id="project_name"
                                type="text"
                                name="project_name"
                                value={projectName}
                                onChange={(e) => setProjectName(e.target.value)}
                                className={styles.inputField}
                            />

                            <button type="submit" className={styles.submitButton}>
                                Create Project
                            </button>
                            <div className={styles["invalid-label"]}>
                            { createError !== "" && <div>{createError}</div>}
                            </div>
                        </form>
                    </Modal>
                </div>
            </div>
        </div>
    );
}