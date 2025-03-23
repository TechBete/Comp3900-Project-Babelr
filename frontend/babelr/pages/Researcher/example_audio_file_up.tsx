import Link from "next/link";
import styles from "stylesheets/projects_list.module.css"
import Navbar from "components/nav_bar";
import Sidebar from "components/side_bar";
import Modal from "components/popout_modal";
import { FormEvent, useEffect, useState } from "react";

// Just a sample audio upload tsx file from Halliya
// I have no clue how this things works in frontend but I know that
// if we use formData, backend will receive files using "request.files"
// I referenced to this frontend code (not perfect or even accurate Ig)
// to build backend side, so please remove it
// after implementing actual frontend code :)

const FileUpload = () => {
    const [file, setFile] = useState<File | null>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setFile(event.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            alert("Please select a file first!");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://localhost:8016/uploadAudioFile", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();
            alert(result.message);
        } catch (error) {
            console.error("Upload failed:", error);
        }
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload</button>
        </div>
    );
};

export default FileUpload;
