import styles from "stylesheets/evaluation.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import { useState, useEffect } from "react";
import { Button } from "@mui/material";
import Slider from '@mui/material/Slider';
import RoleCheck from "components/role_checker";

export default function Evaluation() {
    const [Error, setError] = useState("");
    const [audioID, setAudioID] = useState('');
    const [audioURL, setAudioURL] = useState('null');
    const [submitted, setSubmitted] = useState(true);
    const [sliderClarity, setSliderClarity] = useState(3);
    const [sliderIntelligibility, setSliderIntelligibility] = useState(3);
    const [sliderNaturalness, setSliderNaturalness] = useState(3);

    // gets new audio once submitted
    useEffect(() => {
        fetchAudioPath();
    }, [submitted]);

    const handleChangeClarity = function (event: any, new_value: number) {
        setSliderClarity(new_value);
    }

    const handleChangeIntelligibility = function (event: any, new_value: number) {
        setSliderIntelligibility(new_value);
    }

    const handleChangeNaturalness = function (event: any, new_value: number) {
        setSliderNaturalness(new_value);
    }

    // gets audio file id from the backend
    const fetchAudioPath = async () => {
        const response = await fetch('http://localhost:8016/listener/getAssignedAudioFile', {
            method:"GET",
            credentials: 'include'
        });

        const res = await response.json();
        const audio_id = res.audio_file;

        setAudioID(audio_id);
        fetchAudioFileData(audio_id);
        fetchAudioFile(audio_id);
    };
    // gets audio file data (metrics)
    const fetchAudioFileData = async (audio_id: string) => {
        const response = await fetch('http://localhost:8016/audio/getAudioFileData', {
            method:"POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({audio_id}),
            credentials: 'include'
        });

        const res = await response.json();
    }
    // gets the audio file itself
    const fetchAudioFile = async (audio_id: string) => {
        const response = await fetch('http://localhost:8016/listener/getAudioFile', {
            method:"POST",
            credentials: 'include',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'audio_id': audio_id}),

        });

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
    };

    // post/submit ratings to the backend
    async function submitRating(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        const body = {audio_id: audioID, ratings: {'Clarity': sliderClarity, 'Intelligibility': sliderIntelligibility, 'Naturalness': sliderNaturalness,}}
    
        try {
            const response = await fetch(`http://localhost:8016/listener/submitRating`, {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
                credentials: 'include'
            });
    
            if (!response.ok) {
                const error = await response.json();
                
                setError(error.error);
            } else {
                if (submitted == true) {
                    setSubmitted(false);
                } else {
                    setSubmitted(true);
                }
            }
        } catch {
            setError("Network Error: Fetch Request Failed");
        }
    }

    const test_metrics = {
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

    const marks_clarity = [
        {
          value: 1,
          label: 'Unclear',
        },
        {
          value: 5,
          label: 'Clear',
        },
    ]

    const marks_intelligibility = [
        {
          value: 1,
          label: 'Unintelligible',
        },
        {
          value: 5,
          label: 'Intelligible',
        },
    ]
    const marks_naturalness = [
        {
          value: 1,
          label: 'Robotic',
        },
        {
          value: 5,
          label: 'Natural',
        },
    ]

    return (
        <RoleCheck requiredRole="listener">
            <div>
                <Navbar_Listener></Navbar_Listener>
                <div className={styles["body"]}>
                    <div className={styles["form-container"]}>
                        <div className={styles["information-container"]}>
                            <div className={styles["header-wrapper"]}>
                                <h1 style={{ fontWeight: 'bold', fontSize: '1.9rem', paddingTop: '10px' }}>Audio Evaluation</h1>
                                <p>Play the audio clip and rate it based on the provided metrics.</p>
                                <form className={styles["login-form"]} method="post" onSubmit={submitRating}>
                                    {<audio 
                                        controls 
                                        id="audio" 
                                        src={audioURL}
                                        style={{
                                            display: 'block',
                                            margin: '5px auto',
                                            maxWidth: '100%',  
                                        }}
                                        ></audio>}
                                    <div>
                                        <div key='Clarity'>
                                        <h2 className='metric-name' style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>
                                            Clarity
                                        </h2>
                                            <h2 className='metric-description'>{test_metrics['Clarity'].description}</h2>
                                            <Slider
                                                value={sliderClarity} 
                                                onChange={handleChangeClarity} 
                                                defaultValue={3} 
                                                step={1} 
                                                min={test_metrics['Clarity'].min} 
                                                max={test_metrics['Clarity'].max} 
                                                id='Clarity' 
                                                marks={marks_clarity} 
                                                sx={{
                                                    width: '80%',
                                                    margin: '0 auto', 
                                                    display: 'block',
                                                    color: "#2b4450",
                                                    "& .MuiSlider-thumb": {
                                                    backgroundColor: "#2b4450",
                                                    "&:hover": {
                                                        backgroundColor: "#1f333c",
                                                    },
                                                    },
                                                    "& .MuiSlider-track": {
                                                    backgroundColor: "#2b4450",
                                                    },
                                                    "& .MuiSlider-rail": {
                                                    backgroundColor: "#cccccc",
                                                    },
                                                    "& .MuiSlider-markLabel": {
                                                        paddingTop: '15px',
                                                    },
                                                    paddingBottom: '40px',
                                                }}/>
                                        </div>
                                        <div key='Intelligibility'>
                                            <h2 className='metric-name' style={{ fontWeight: 'bold', fontSize: '1.2rem', paddingTop: '30px' }}>
                                                Intelligibility
                                            </h2>
                                            <h2 className='metric-description'>{test_metrics['Intelligibility'].description}</h2>
                                            <Slider 
                                                value={sliderIntelligibility} 
                                                onChange={handleChangeIntelligibility} 
                                                defaultValue={3} 
                                                step={1} 
                                                min={test_metrics['Intelligibility'].min} 
                                                max={test_metrics['Intelligibility'].max} 
                                                id='Intelligibility' 
                                                marks={marks_intelligibility} 
                                                sx={{
                                                    width: '80%',
                                                    margin: '0 auto', 
                                                    display: 'block',
                                                    color: "#2b4450",
                                                    "& .MuiSlider-thumb": {
                                                    backgroundColor: "#2b4450",
                                                    "&:hover": {
                                                        backgroundColor: "#1f333c",
                                                    },
                                                    },
                                                    "& .MuiSlider-track": {
                                                    backgroundColor: "#2b4450",
                                                    },
                                                    "& .MuiSlider-rail": {
                                                    backgroundColor: "#cccccc",
                                                    },
                                                    "& .MuiSlider-markLabel": {
                                                        paddingTop: '15px',
                                                    },
                                                    paddingBottom: '40px',
                                                }}/>
                                        </div>
                                        <div key='Naturalness'>
                                        <h2 className='metric-name' style={{ fontWeight: 'bold', fontSize: '1.2rem', paddingTop: '30px' }}>
                                            Naturalness
                                        </h2>
                                            <h2 className='metric-description'>{test_metrics['Naturalness'].description}</h2>
                                            <Slider
                                                value={sliderNaturalness} 
                                                onChange={handleChangeNaturalness} 
                                                defaultValue={3} 
                                                step={1} 
                                                min={test_metrics['Naturalness'].min} 
                                                max={test_metrics['Naturalness'].max} 
                                                id='Naturalness' 
                                                marks={marks_naturalness}
                                                sx={{
                                                    width: '80%',
                                                    margin: '0 auto', 
                                                    display: 'block',
                                                    color: "#2b4450",
                                                    "& .MuiSlider-thumb": {
                                                    backgroundColor: "#2b4450",
                                                    "&:hover": {
                                                        backgroundColor: "#1f333c",
                                                    },
                                                    },
                                                    "& .MuiSlider-track": {
                                                    backgroundColor: "#2b4450",
                                                    },
                                                    "& .MuiSlider-rail": {
                                                    backgroundColor: "#cccccc",
                                                    },
                                                    "& .MuiSlider-markLabel": {
                                                        paddingTop: '15px',
                                                    },
                                                    paddingBottom: '40px',
                                                }}/>
                                        </div>
                                    </div>
                                    <Button
                                        variant="contained"
                                        type="submit"
                                        sx={{
                                            backgroundColor: "#2b4450",
                                            "&:hover": {
                                            backgroundColor: "#1f333c",
                                            },
                                            display: "block",           
                                            margin: "30px auto 0",   
                                        }}>
                                            Submit Rating
                                    </Button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </RoleCheck>
    );
}