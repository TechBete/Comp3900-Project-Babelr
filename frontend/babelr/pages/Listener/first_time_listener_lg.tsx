import { useState, FormEvent } from "react";
import styles from "stylesheets/first_time_listener.module.css";
import Image from "next/image";
import { useRouter } from "next/router";

type LanguageEntry = {
    language: string;
    proficiency: string;
};

export default function LanguageSelector() {
    const [languages, setLanguages] = useState<LanguageEntry[]>([]);
    const [error, setError] = useState("");
    const router = useRouter();

    const handleChange = (index: number, field: keyof LanguageEntry, value: string) => {
        const newLanguages = [...languages];
        newLanguages[index][field] = value;
        setLanguages(newLanguages);
    };

    const addLanguage = () => {
        setLanguages([...languages, { language: "", proficiency: "" }]);
    };

    const removeLanguage = (index: number) => {
        const updated = [...languages];
        updated.splice(index, 1);
        setLanguages(updated);
    };

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();

        let allSuccessful = true;

        for (const entry of languages) {
            const success = await postLanguage(entry);
            if (!success) {
                allSuccessful = false;
            }
        }
    
        if (allSuccessful) {
            router.push("/listenerhomepage");
        }
    };

    const postLanguage = async (entry: LanguageEntry): Promise<boolean> => {
        try {
            const response = await fetch("http://localhost:8016/listener/addLanguage", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(entry),
            });

            if (!response.ok){
                const data = await response.json();
                setError(data.error || "Error posting language");
                return false;
            }

            return true;
        } catch {
            setError("Network Error: Fetch Request Failed");
            return false;
        }
    };

    return (
        <div className={styles["body"]}>
            <div className={styles["form-container"]}>
                <div className={styles["information-container"]}>
                    <div className={styles["header-wrapper"]}>
                        <h1>Select Your Languages</h1>
                        <p>Add languages and your proficiency level</p>
                        <form onSubmit={handleSubmit}>
                        <div className={styles["language-box"]}>
                            {languages.map((entry, index) => (
                                <div key={index} style={{ display: "flex", gap: "10px", marginBottom: "10px", alignItems: "center" }}>
                                    <select
                                        value={entry.language}
                                        onChange={(e) => handleChange(index, "language", e.target.value)}
                                        className={styles.select}
                                        required
                                    >
                                    <option value="">Language</option>
                                    {["English", "Spanish", "French", "Mandarin", "Hindi", "Arabic", "Other"].map((lang) => ( // change to saved list of languages later
                                        <option
                                            key={lang}
                                            value={lang}
                                            disabled={languages.some((e, i) => e.language === lang && i !== index)}
                                        >
                                            {lang}
                                        </option>
                                    ))}
                                    </select>

                                    <select
                                        value={entry.proficiency}
                                        onChange={(e) => handleChange(index, "proficiency", e.target.value)}
                                        className={styles.select}
                                        required
                                    >
                                        <option value="">Proficiency</option>
                                        <option>Beginner</option>
                                        <option>Intermediate</option>
                                        <option>Advanced</option>
                                        <option>Native</option>
                                    </select>

                                    <button type="button" onClick={() => removeLanguage(index)} style={{ background: "transparent", border: "none", fontSize: "1.2em", cursor: "pointer" }}>
                                        ✕
                                    </button>
                                </div>
                            ))}
                        </div>

                        <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                            <button type="button" onClick={addLanguage} className={styles.button}>
                                Add Language
                            </button>
                            <button type="submit" className={styles.button}>
                                Next
                            </button>
                        </div>
                            {error && <div className="error-label">{error}</div>}
                        </form>
                    </div>
                </div>
            </div>
            <div className={styles["image-container"]}>
                <Image src="/babelr_logo.png" alt="side-image" width={1024} height={1024}/>
            </div>
        </div>
    );
}