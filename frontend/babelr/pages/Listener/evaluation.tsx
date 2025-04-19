import styles from "stylesheets/evaluation.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import { useState, useEffect } from "react";
import { Button } from "@mui/material";
import Slider from '@mui/material/Slider';

export default function Evaluation() {
    const [Error, setError] = useState("");
    const [audioPath, setAudioPath] = useState("");
    const [audioFile, setAudioFile] = useState('null');

    const fetchAudioPath = async () => {
        const response = await fetch('http://127.0.0.1:8016/listener/getAssignedAudioFile', {
            method:"GET",
            credentials: 'include'
        });

        const res = await response.json();

        console.log('res: ', res.audio_file);
        // setAudioPath(res);
        setAudioPath(res.audio_file);
        console.log("audio path is: ", audioPath);
    };

    const fetchAudioFileData = async () => {
        const obj = filter_audio_path();
        console.log('obj: ', obj);
        const project_name = obj['project_name']; // 'project name 2'; // 
        const audio_file_name = obj['audio_file_name']; // 'audio file name 3'; // 

        const response = await fetch('http://127.0.0.1:8016/audio/getAudioFileData', {
            method:"POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({project_name, audio_file_name}),
            credentials: 'include'
        });

        const res = await response.json();

        setAudioFile('hello world');

        console.log(audioFile);
        console.log('res: ', res);
    }

    const filter_audio_path = function() {
        // example = '/app/audioData/c1056c9e-962c-499d-83a8-599e784a4109/water bottle 1/temp_fntemp_ln/ch_2.wav'
        const parts = audioPath.split('/');
        const project_name = parts[4];
        const audio_file_name = parts[parts.length - 1];

        return { project_name, audio_file_name };
    }

    useEffect(() => {
        fetchAudioPath();
        fetchAudioFileData();
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

    const test_metrics = [
        {'name': 'Clarity', 'description': 'How clear is the speech?'},
        {'name': 'Intelligibility', 'description': 'How easy to understand is the speech?'}
    ]

    const marks = [
        {
          value: 1,
          label: '1',
        },
        {
          value: 5,
          label: '5',
        },
      ];

    const metric_grid = test_metrics.map((metric) => (
        <div key={metric.name}>
            <h2 className='metric-name'>{metric.name}</h2>
            <h2 className='metric-description'>{metric.description}</h2>
            <Slider defaultValue={3} step={1} min={1} max={5} id={metric.name} valueLabelDisplay="auto" marks={marks} />
        </div>
    ));

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
                                {/*audioUrl && <audio controls src={audioUrl}></audio>*/}
                                {<audio controls id="audio" src="/ch_0.wav"></audio>}
                                {/*<Button variant="contained" id='playButton'>Play</Button>*/}
                                {metric_grid}
                                <Button variant="contained" type='submit'>Submit Rating</Button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}