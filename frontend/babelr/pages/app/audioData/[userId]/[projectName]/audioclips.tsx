import { useState, FormEvent, ChangeEvent, useEffect } from "react";
import { useRouter } from 'next/router';
import Navbar from "components/nav_bar_researcher";
// import Sidebar from "components/side_bar";
import Sidebar from "components/project_sidebar"
import Modal from "components/popout_modal";
import styles from "stylesheets/file_upload.module.css";
// import AudioClipsTable from "components/clips_table";
import {Box, Button} from "@mui/material";

import TableTest from "components/table";
import RoleCheck from "components/role_checker";

interface AudioData {
    name: string;
    tags: string[];
    dateAdded: string;
    evaluated: string;
    rating: number;
}

type RawAudioClip = {
    name: string;
    tags: string[]; // update this based on actual structure if needed
    Researcher: string;
    file_extension: string;
    file_path: string;
    allocated_listeners: never[];
    project_name: string;
    project_path: string;
    metrics: never; // or type it properly if you use it
};


enum LangProf {
    none = 'none_set',
    elementary = 'elementary',
    limited_working = 'limited_working',
    professional = 'professional',
    native = 'native',
    bilingual = 'bilingual',
}


export default function FileUploadPage() {
    const router = useRouter();
    const { projectName } = router.query; //  project name
    console.log(projectName)

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [fileName, setFileName] = useState("");
    const [tags, setTags] = useState("");
    const [model, setModel] = useState("");
    const [language, setLanguage] = useState("");
    const [langProf, setLangProf] = useState<LangProf>(LangProf.none)
    const [uploadError, setUploadError] = useState("");
    const [audioData, setAudioData] = useState<AudioData[]>([]);
    const [isStarted, setIsStarted] = useState(false);
    

    useEffect(() => {
        if (typeof projectName === 'string') {
            getAudioClips();
        }
    }, [projectName]); // <- only runs when projectName changes

    if (typeof projectName !== 'string') {
        return <div>Loading?</div>;
    }

    async function getAudioClips() {
        console.log('project name is ',JSON.stringify({project_name: projectName}))
        try {
            const response = await fetch('http://localhost:8016/audio/getProjectAudioFiles' , {
                method:"POST",
                credentials: 'include',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({project_name: projectName}),
            })
            
            if (response.ok) {
                const { audio_files }: { audio_files: RawAudioClip[] } = await response.json();
                console.log('raw audioClips:', audio_files);
                const formattedClips: AudioData[] = audio_files.map(clip => ({
                    name: clip.name,
                    tags: clip.tags?.map(tag => tag.trim()).filter(Boolean) ?? [],
                    dateAdded: new Date().toLocaleDateString(),
                    evaluated: "0/50",
                    rating: 0,
                }));
                setAudioData(formattedClips);
                console.log('clips are',formattedClips)
            } else {
                const error = await response.json()
                console.log(error)
            }
        } catch {

        }
    } 
    

    function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
        if (event.target.files && event.target.files.length > 0) {
            const selectedFile = event.target.files[0];
            setFile(selectedFile);
            setFileName(selectedFile.name.replace(/\.[^/.]+$/, "")); // Remove file extension
        }
    }

    async function handleUpload(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!file || fileName.trim() === "") {
            setUploadError("Please select a file and provide a name.");
            return;
        }

        const fileExtension = file.name.split(".").pop(); // Keep original extension
        const newFileName = `${fileName}.${fileExtension}`;
        const combinedTags = [model, language, langProf, tags].filter(Boolean).join(",");

        const formData = new FormData();
        formData.append("file", file);
        formData.append("fileName", newFileName);
        formData.append("tags", combinedTags);
        if (typeof projectName === 'string') {
            formData.append("project_name", projectName);
        }

        for (const [key, value] of formData.entries()) {
            console.log(`${key}:`, value);
          }

        try {
            const response = await fetch("http://localhost:8016/audio/uploadAudioFile", {
                method: "POST",
                body: formData,
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error("Upload failed.");
            }

            const result = await response.json();
            console.log("Upload successful:", result);

            getAudioClips()
            setIsModalOpen(false);
            setFile(null);
            setFileName("");
            setTags("");
            setUploadError("");

        } catch (error) {
            console.error("Error uploading file:", error);
            setUploadError("Upload failed. Please try again.");
        }
    }

    return (
        <RoleCheck requiredRole="researcher">
            <div className={styles.projectBody}>
                <Navbar />
                <div className={styles.container}>
                    <Sidebar project_name={projectName}></Sidebar>
                    <div className={styles.mainContent}>
                        <h2 className={styles.heading}>Audio Library</h2>

                        {/* Metrics Section */}
                        <div className={styles.metricsContainer}>
                            <div className={styles.metricBox}>
                                <h3>Total Audio Clips</h3>
                                <p>{audioData.length}</p>
                            </div>
                            <div className={styles.metricBox}>
                                <h3>Average Rating</h3>
                                <p>{(audioData.reduce((sum, audio) => sum + audio.rating, 0) / audioData.length || 0).toFixed(2)}</p>
                            </div>
                            <div className={styles.metricBox}>
                                <h3>Evaluated Clips</h3>
                                <p>{audioData.filter(audio => audio.evaluated !== "0/50").length}</p>
                            </div>
                        </div>

                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'flex-end' }}>
                            <Button className={`${styles.startButton} ${isStarted ? styles.inProgress : ''}`} sx={{ marginLeft: "auto" }}  onClick={() => setIsStarted(!isStarted)}>
                                {isStarted ? "In Progress" : "Start"} 
                            </Button>
                            <Button className={styles.addAudioBtn} sx={{ marginLeft: "20px" }}  onClick={() => setIsModalOpen(true)}> + </Button>
                        </Box>

                        <TableTest audioData={audioData}></TableTest>
                        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} hasCloseBtn>
                            <h2 className={styles.modalTitle}>Upload New Audio</h2>

                            <form onSubmit={handleUpload}>
                                <label className={styles.formLabel}>Choose File</label>
                                <input 
                                    type="file" 
                                    accept="audio/*" 
                                    className={styles.fileInput} 
                                    onChange={handleFileChange} 
                                />

                            <label className={styles.formLabel}>Model</label>
                                <input
                                    type="text"
                                    value={model}
                                    onChange={(e) => setModel(e.target.value)}
                                    className={styles.inputField}
                                    required
                                />

                                <label className={styles.formLabel}>Language</label>
                                    <select
                                        value={language}
                                        onChange={(e) => setLanguage(e.target.value)}
                                        className={styles.inputField}
                                        required
                                    >
                                        <option value="">Language</option>
                                        {["English", "Spanish", "French", "Mandarin", "Hindi", "Arabic", "Other"].map((lang) => (
                                        <option key={lang} value={lang}>
                                            {lang}
                                        </option>
                                        ))}
                                    </select>

                                <label className={styles.formLabel}>Language Proficiency</label>
                                    <select
                                        value={langProf}
                                        onChange={(e) => setLangProf(e.target.value as LangProf)}
                                        className={styles.inputField}
                                        required
                                    >
                                        {Object.values(LangProf).map((level) => (
                                            <option key={level} value={level}>
                                                {level.replace('_', ' ')}
                                            </option>
                                        ))}
                                </select>

                                <label className={styles.formLabel}>Tags (comma separated)</label>
                                <input
                                    type="text"
                                    value={tags}
                                    onChange={(e) => setTags(e.target.value)}
                                    className={styles.inputField}
                                />

                                
                                <button type="submit" className={styles.submitButton}>Upload</button>
                                {uploadError && <div className={styles.invalidLabel}>{uploadError}</div>}
                            </form>
                        </Modal>
                    </div>
                </div>
            </div>
        </RoleCheck>
    );
}
