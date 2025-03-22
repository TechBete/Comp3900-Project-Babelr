import Link from "next/link";
import styles from "../stylesheets/projects_list.module.css"
import Navbar from "../components/nav_bar";
import Sidebar from "../components/side_bar";
import Modal from "../components/popout_modal";
import { FormEvent, useEffect, useState } from "react";



function Project({ name, path, status, creator } : { name: string; path: string; status: string; creator: string }) {
    
    const StatusStyle = () => {
        if (status == "in-progress") {
            return <td className={styles["td"]}><span className={`${styles.status} ${styles["in-progress"]}`}>In Progress</span></td>
        } else if (status == "complete") {
            return <td className={styles["td"]}><span className={`${styles.status} ${styles["complete"]}`}>Complete</span></td>
        } else if (status == "Draft") {
            return <td className={styles["td"]}><span className={`${styles.status} ${styles["draft"]}`}>Draft</span></td>
        }
    };

    return (
        <tr className={styles["tr"]}>
            <td className={styles["td"]}><Link className={styles["projects-link"]} href={path}>{name}</Link></td>
            {StatusStyle()}
            <td className={styles["td"]}>{creator}</td>
        </tr>
    );
}

function ProjectList({ projects }: { projects: { name: string; path: string; status: string; creator: string }[] }) {
    return (
        <tbody>
            {projects.map((project_dict, index) => (
                <Project key={index} {...project_dict} />
            ))}
        </tbody>
    );
}



export default function MainScreen() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [projectName, setProjectName] = useState("Project_4"); // change this to empty string later for production
    const [createError, setCreateError] = useState("");
    const [projectsData, setProjectData] = useState([]);
    useEffect(() => {
        getProjects();
        // setProjectData([]);
    }, [])

    async function getProjects() {
        try {
            const response = await fetch('http://localhost:8016/getProjects' , {
                method:"GET",
                credentials: 'include'
            })
            if (response.ok) {
                const project_list = await response.json();
                setProjectData(project_list.projects_list);
                console.log(project_list)
            } else {
                const error = await response.json()
                console.log(error)
            }
        } catch {

        }
    } 

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
				const data = await response.json();
                console.log(data.message);
                getProjects();
			} else {
                const error = await response.json()
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
                    <table className={styles["table"]} >
                        <thead className={styles["thead"]}>
                            <tr className={styles["tr"]}>
                                <th className={styles["th"]}>Name</th>
                                <th className={styles["th"]}>Status</th>
                                <th className={styles["th"]}>Creator</th>
                                <th className={styles["th"]}></th>
                            </tr>
                        </thead>
                        <ProjectList projects={projectsData}/>
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