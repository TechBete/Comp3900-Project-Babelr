import { useState, FormEvent, ChangeEvent } from "react";
import Navbar from "../components/nav_bar";
import Sidebar from "../components/side_bar";
import Modal from "../components/popout_modal";
import styles from "../stylesheets/file_upload.module.css";

interface AudioData {
    name: string;
    tags: string[];
    dateAdded: string;
    evaluated: string;
    rating: number;
}

export default function FileUploadPage() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [fileName, setFileName] = useState("");
    const [tags, setTags] = useState("");
    const [uploadError, setUploadError] = useState("");
    const [audioData, setAudioData] = useState<AudioData[]>([
        { name: "Screaming.mp3", tags: ["Fast Speech", "Child"], dateAdded: "2/5/2025", evaluated: "48/50", rating: 3.6 },
        { name: "Asong.wav", tags: ["Style Speech", "Adult"], dateAdded: "5/4/2025", evaluated: "30/50", rating: 2.375 }
    ]);

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

        const formData = new FormData();
        formData.append("file", file);
        formData.append("fileName", newFileName);
        formData.append("tags", tags);

        try {
            const response = await fetch("http://localhost:8016/projects/uploadAudioFile", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Upload failed.");
            }

            const result = await response.json();
            console.log("Upload successful:", result);

            // Update state with the new audio file
            const newAudio: AudioData = {
                name: newFileName,
                tags: tags.split(",").map(tag => tag.trim()).filter(tag => tag),
                dateAdded: new Date().toLocaleDateString(),
                evaluated: "0/50",
                rating: 0
            };

            setAudioData([...audioData, newAudio]);
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
        <div className={styles.projectBody}>
            <Navbar />
            <div className={styles.container}>
                <Sidebar />
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

                    <button className={styles.addAudioBtn} onClick={() => setIsModalOpen(true)}> + </button>

                    <table className={styles.table}>
                        <thead>
                            <tr>
                                <th>Audio Clips</th>
                                <th>Tags</th>
                                <th>Date Added</th>
                                <th>Evaluated</th>
                                <th>Rating</th>
                            </tr>
                        </thead>
                        <tbody>
                            {audioData.map((audio, index) => (
                                <tr key={index} className={styles.tr}>
                                    <td className={styles.td}><a href="#">{audio.name}</a></td>
                                    <td className={styles.td}>{audio.tags.join(", ")}</td>
                                    <td className={styles.td}>{audio.dateAdded}</td>
                                    <td className={styles.td}>{audio.evaluated}</td>
                                    <td className={styles.td}>{audio.rating}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

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

                            {file && (
                                <>
                                    <label className={styles.formLabel}>File Name</label>
                                    <input
                                        type="text"
                                        value={fileName}
                                        onChange={(e) => setFileName(e.target.value)}
                                        className={styles.inputField}
                                    />
                                </>
                            )}

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
    );
}
