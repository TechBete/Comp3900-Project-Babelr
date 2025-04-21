import styles from "stylesheets/evaluation.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import { useState, useEffect } from "react";
import { Button } from "@mui/material";
import Slider from '@mui/material/Slider';

export default function Evaluation() {
    const [Error, setError] = useState("");
    const [audioURL, setAudioURL] = useState('null');
    const [metricsObj, setMetricsObj] = useState({});

    const fetchAudioPath = async () => {
        const response = await fetch('http://localhost:8016/listener/getAssignedAudioFile', {
            method:"GET",
            credentials: 'include'
        });

        const res = await response.json();
        fetchAudioFileData(res.audio_file);
    };

    const fetchAudioFileData = async (audio_path: string) => {
        const obj = filter_audio_path(audio_path);
        const project_name = obj['project_name'];
        const audio_file_name = obj['audio_file_name'];

        const response = await fetch('http://localhost:8016/audio/getAudioFileData', {
            method:"POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({project_name, audio_file_name}),
            credentials: 'include'
        });

        const res = await response.json();

        setMetricsObj(res.audio_file.metrics);
        fetchAudioFile();
    }

    const fetchAudioFile = async () => {
        const response = await fetch('http://localhost:8016/listener/getAudioFile', {
            method:"GET",
            credentials: 'include'
        });

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
    };

    const filter_audio_path = function(audio_path: string) {
        // example = '/app/audioData/c1056c9e-962c-499d-83a8-599e784a4109/water bottle 1/temp_fntemp_ln/ch_2.wav'
        const parts = audio_path.split('/');
        const project_name = parts[4];
        const audio_file_name = parts[parts.length - 1];

        return { project_name, audio_file_name };
    }

    const metric_object_to_array = function (metric_obj: object) {
        const metric_array: any[] = [];

        Object.entries(metric_obj).forEach(([key, value]) => {
            const mini_obj = {'name': key, ...value};
            metric_array.push(mini_obj);
        });

        return metric_array;
    }

    useEffect(() => {
        fetchAudioPath();
    }, []);

    async function submitRating() {
        console.log("Submit rating was hit!!!")
        try {
            const response = await fetch(`http://localhost:8016/listener/submitRating`, {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({"id": 2, 'ratings': [{'clarity': 4}, {'fluency': 2}]}),
                credentials: 'include'
            })

            if (response.ok) {
                // const response = await response.json()
                return // change later maybe
            } else {
                const error = await response.json();
                setError(error.error);
            }

        } catch {
            console.log("There was a network error unforunate/1111");
            setError("Network Error: Fetch Request Failed");
            return Error;
        }
    }

    /*
    const test_metrics_1 = [
        {'name': 'Clarity', 'description': 'How clear is the speech?'},
        {'name': 'Intelligibility', 'description': 'How easy to understand is the speech?'}
    ]
    */

    const test_metrics_2 = {
        "Clarity": {
            "description": "How clear the audio sounds",
            "max": 5,
            "maximum label": "Clear",
            "min": 1,
            "minimum label": "Unclear"
        },
        "Intelligibility": {
            "description": "How easy it is to understand the audio",
            "max": 5,
            "maximum label": "Intelligible",
            "min": 1,
            "minimum label": "Unintelligible"
        },
        "Naturalness": {
            "description": "How natural the audio sounds",
            "max": 5,
            "maximum label": "Natural",
            "min": 1,
            "minimum label": "Robotic"
        }
    }

    const metrics_array = metric_object_to_array(metricsObj);
    const metric_grid_2 = metrics_array.map((metric) => {
        return (
            <div key={metric.name}>
                <h2 className='metric-name'>{metric.name}</h2>
                <h2 className='metric-description'>{metric.description}</h2>
                <Slider defaultValue={3} step={1} min={metric.min} max={metric.max} id={metric.name} valueLabelDisplay="auto" marks={[{value: metric.min, label: metric['minimum label']}, {value: metric.max, label: metric['maximum label']}]} />
            </div>
        )
    });

    return (
        <div>
            <Navbar_Listener></Navbar_Listener>
            <div className={styles["body"]}>
                <div className={styles["form-container"]}>
                    <div className={styles["information-container"]}>
                        <div className={styles["header-wrapper"]}>
                            <h1>Evaluation</h1>
                            <p>Play the audio clip and rate it based on the provided metrics.</p>
                            <form className={styles["login-form"]} method="post" onSubmit={submitRating}>
                                {<audio controls id="audio" src="/ch_0.wav"></audio>}
                                <Button variant="contained" type='submit'>Submit Rating</Button>
                                {metric_grid_2}
                                {<audio controls id="audio" src={audioURL}></audio>}
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}