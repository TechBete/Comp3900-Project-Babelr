import Link from "next/link";
import styles from "../stylesheets/projects_list.module.css"
import Navbar from "../components/nav_bar";
import Sidebar from "../components/side_bar";

export default function MainScreen() {
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

                    <button className={styles["add-project-btn"]}> + </button>
                </div>
            </div>
        </div>
    );
}