import styles from "../stylesheets/side_bar.module.css"

// interface SidebarProps {
//     variant?: "projects" | "in_projects"
// }

export default function Sidebar() {

    return (
        <div className={styles["sidebar"]}>
            <div className={styles["sidebar-header"]}>
                {/* {variant === "projects" ? "Projects" : variant === "in_projects" ? } */}
                Projects
            </div>
            <ul>
                <li className={styles["active"]}>My Projects</li>
            </ul>
        </div>
    );
}
