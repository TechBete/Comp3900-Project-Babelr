import styles from "stylesheets/evaluation.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import { useState, useEffect } from "react";
import { Button } from "@mui/material";
import Slider from '@mui/material/Slider';

export default function Evaluation() {
    const [Error, setError] = useState("");
    const [audioID, setAudioID] = useState('');
    const [audioURL, setAudioURL] = useState('null');
    const [metricsObj, setMetricsObj] = useState({});
    const [submitted, setSubmitted] = useState(true);
    // const [sliders, setSliders] = useState({});
    const [sliderClarity, setSliderClarity] = useState(3);
    const [sliderIntelligibility, setSliderIntelligibility] = useState(3);
    const [sliderNaturalness, setSliderNaturalness] = useState(3);
    
    const [sliders, setSliders] = useState({
        Clarity: 3,
        Intelligibility: 3, 
        Naturalness: 3,
    });
    
    const [value, setValue] = useState(3);

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

    const handleSliderChange = (metric: string) => (_: any, new_value: number) => {
        // sliders[metric] = new_value

        setSliders((sliders: any) => ({
            ...sliders,
            [metric]: new_value,
        }));

        // setValue(sliders);
    };

    const fetchAudioPath = async () => {
        const response = await fetch('http://localhost:8016/listener/getAssignedAudioFile', {
            method:"GET",
            credentials: 'include'
        });

        const res = await response.json();
        const audio_id = res.audio_file;
        console.log("AUDIO ID OBTAINED FROM QUEUE ", audio_id)
        setAudioID(audio_id);
        fetchAudioFileData(audio_id);
        fetchAudioFile(audio_id);
    };

    const fetchAudioFileData = async (audio_id: string) => {
        const response = await fetch('http://localhost:8016/audio/getAudioFileData', {
            method:"POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({audio_id}),
            credentials: 'include'
        });

        const res = await response.json();

        setMetricsObj(res.audio_file.metrics);
    }

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

    const metric_object_to_array = function (metric_obj: object) {
        const metric_array: any[] = [];

        Object.entries(metric_obj).forEach(([key, value]) => {
            const mini_obj = {'name': key, ...value};
            metric_array.push(mini_obj);
        });

        return metric_array;
    }

    async function submitRating(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault(); 
    
        console.log("Submit rating was hit!!!", sliders);
        console.log('audioId and ratings', { audioID, ratings: sliders });
    
        try {
            const response = await fetch(`http://localhost:8016/listener/submitRating`, {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ audio_id: audioID, ratings: sliders }),
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
            console.log("There was a network error unfortunate/1111");
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

    /*
    function getValueSafe<T extends object>(obj: T, key: keyof T): T[keyof T] | undefined {
        return key in obj ? obj[key] : undefined;
    }
    */

    const metrics_array = metric_object_to_array(metricsObj);

    /*
    for (const [key, value] of Object.entries(metrics_array)) {
        setSliders((sliders: any) => ({
            ...sliders,
            [key]: {'rating': 3, ...value},
        }));
    }

    const new_metric_grid = sliders.map((metric: object) => {
        const marks = [{value: metric.min, label: metric['minimum label']}, {value: metric.max, label: metric['maximum label']}]
        // const metric_name: string = metric.name
        // const val: number = sliders[metric_name as keyof string];
        const val = getValueSafe(sliders, metric.name)

        return (
            <div key={metric.name}>
                <h2 className='metric-name'>{metric.name}</h2>
                <h2 className='metric-description'>{metric.description}</h2>
                <Slider value={val} onChange={handleSliderChange(metric.name)} defaultValue={3} step={1} min={metric.min} max={metric.max} id={metric.name} marks={marks} />
            </div>
        )
    });

    const metric_grid = metrics_array.map((metric) => {
        const marks = [{value: metric.min, label: metric['minimum label']}, {value: metric.max, label: metric['maximum label']}]
        // const metric_name: string = metric.name
        // const val: number = sliders[metric_name as keyof string];
        const val = getValueSafe(sliders, metric.name)

        return (
            <div key={metric.name}>
                <h2 className='metric-name'>{metric.name}</h2>
                <h2 className='metric-description'>{metric.description}</h2>
                <Slider value={val} onChange={handleSliderChange(metric.name)} defaultValue={3} step={1} min={metric.min} max={metric.max} id={metric.name} marks={marks} />
            </div>
        )
    });
    */

    /*
    const metric_grid = metrics_array.map((metric) => {
        const marks = [{value: metric.min, label: metric['minimum label']}, {value: metric.max, label: metric['maximum label']}]
        // const metric_name: string = metric.name
        // const val: number = sliders[metric_name as keyof string];
        // const val = getValueSafe(sliders, metric.name)

        return (
            <div key={metric.name}>
                <h2 className='metric-name'>{metric.name}</h2>
                <h2 className='metric-description'>{metric.description}</h2>
                <Slider value={val} onChange={handleSliderChange(metric.name)} defaultValue={3} step={1} min={metric.min} max={metric.max} id={metric.name} marks={marks} />
            </div>
        )
    });
    */

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

    const metric_grid_2 = function() {
        <div>
            <div key='Clarity'>
                <h2 className='metric-name'>Clarity</h2>
                <h2 className='metric-description'>{test_metrics['Clarity'].description}</h2>
                <Slider value={sliders.Clarity} onChange={handleChangeClarity} defaultValue={3} step={1} min={test_metrics['Clarity'].min} max={test_metrics['Clarity'].max} id='Clarity' marks={marks_clarity} />
            </div>
            <div key='Intelligibility'>
                <h2 className='metric-name'>Intelligibility</h2>
                <h2 className='metric-description'>{test_metrics['Intelligibility'].description}</h2>
                <Slider value={sliders.Intelligibility} onChange={handleChangeIntelligibility} defaultValue={3} step={1} min={test_metrics['Intelligibility'].min} max={test_metrics['Intelligibility'].max} id='Intelligibility' marks={marks_intelligibility} />
            </div>
            <div key='Naturalness'>
                <h2 className='metric-name'>Naturalness</h2>
                <h2 className='metric-description'>{test_metrics['Naturalness'].description}</h2>
                <Slider value={sliders.Naturalness} onChange={handleChangeNaturalness} defaultValue={3} step={1} min={test_metrics['Naturalness'].min} max={test_metrics['Naturalness'].max} id='Naturalness' marks={marks_naturalness} />
            </div>
        </div>
    }

    return (
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
    );
}