import Link from "next/link";
import styles from "stylesheets/projects_list.module.css"
import Navbar from "components/nav_bar_researcher";
import Modal from "components/popout_modal";
import CreateButton from "components/create_button";
import { FormEvent, useEffect, useState } from "react";
import RoleCheck from "components/role_checker";



// displays each project in individual rows
function Project({ project_name, path, status, creator_name } : { project_name: string; path: string; status: string; creator_name: string }) {
    console.log('status is', status);
    const StatusStyle = () => {
        if (status == "in_progress") {
            return <td className={styles["td"]}><span className={`${styles.status} ${styles["in-progress"]}`}>In Progress</span></td>
        }  else if (status == "draft") {
            return <td className={styles["td"]}><span className={`${styles.status} ${styles["draft"]}`}>Draft</span></td>
        }
    };

    return (
        <tr className={styles["tr"]}>
            <td className={styles["td"]}><Link className={styles["projects-link"]} href={`${path}/audioclips`}>{project_name}</Link></td>
            {StatusStyle()}
            <td className={styles["td"]}>{creator_name}</td>
        </tr>
    );
}
// displays the whole list of projects
function ProjectList({ projects }: { projects: { project_name: string; path: string; status: string; creator_name: string }[] }) {
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
    const [projectName, setProjectName] = useState("");
    const [createError, setCreateError] = useState("");
    const [projectsData, setProjectData] = useState([]);

    useEffect(() => {
        getProjects();
    }, [])
    // gets the list of projects from the backend
    async function getProjects() {
        try {
            const response = await fetch('http://localhost:8016/projects/getProjects' , {
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
    // handles creating a new project
    async function handleCreate(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        try {
            const response = await fetch('http://localhost:8016/projects/createProject', {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({"project_name": projectName}),
                credentials: 'include'
            })
        
            if (response.ok) {
				const data = await response.json();
                console.log(data.message);
                getProjects();
                setIsModalOpen(false);
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
        <RoleCheck requiredRole="researcher">
            <div className={styles["project-body"]}>
                < Navbar/>
                <div className={styles["container"]}>
                    <div className={styles["main-content"]}>
                        <div className={styles["main-top"]}>
                            <h2 className={styles["projects-h2"]}>
                                Your Projects     
                            </h2>
                        </div>
                        {/* displays the list of projects */}
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
                        {/* modal to create a new project */}
                        <CreateButton onClick={() => setIsModalOpen(true)}></CreateButton>
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
        </RoleCheck>
    );
}
