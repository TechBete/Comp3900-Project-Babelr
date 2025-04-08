import styles from "stylesheets/evaluation.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import { useState, useEffect } from "react";
import { Button } from "@mui/material";
import Slider from '@mui/material/Slider';
// import Box from '@mui/material/Box';

export default function Evaluation() {
    const [Error, setError] = useState("");
    // const [value, setValue] = useState(3);

    useEffect(() => {
        Audio_Receiver();
        /*
        const el = document.getElementById("audio");

        if (el != null) {
            el.addEventListener("click", playAudio, false);
            // el.attachEvent('onclick', playAudio);
        }
        */
    });

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
                console.log("HAHAHAHAHA!!!");
                // const response = await response.json()
                return // change later maybe
            } else {
                console.log("Banana!!");
                const error = await response.json();
                setError(error.error);
            }

        } catch {
            console.log("There was a network error unforunate/1111");
            setError("Network Error: Fetch Request Failed");
            return Error;
        }
    }

    async function Audio_Receiver() {
        try {
            const response = await fetch(`http://localhost:8016/audioAllocate`, {
                method:"GET",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({}),
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
            setError("Network Error: Fetch Request Failed");
            return Error;
        }
    }

    /*
    function playAudio() {
        const audio_el = document.querySelectorAll('audio'); // .getElementById('audio')
        
        if (audio_el[0] != null) {
            audio_el[0].play(); // eslint-disable-line
        }
    }
    */

    /*
    function valuetext(value: number) {
        return `${value}°C`;
    }
    */

    // const test_metric_names = ["Clarity", "Intelligibility"];
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
                                <audio controls id="audio" src="ch_0.wav"></audio>
                                {/*<Button variant="contained" id='playButton'>Play</Button>*/}
                                {metric_grid}

                                {/*<h2>Clarity</h2> 
                                <Slider defaultValue={3} step={1} marks min={1} max={5} />*/}

                                {/*<button id='playButton'>Play Audio</button>*/}
                                {/*
                                <div>
                                    <h2 className="text-xl font-semibold">Value: {value}</h2>
                                    <Slider
                                        value={[value]}
                                        onValueChange={(val) => setValue(val[0])}
                                        min={0}
                                        max={5}
                                        step={1}
                                        className="w-64"
                                    />
                                </div>
                                */}
                                <Button variant="contained" type='submit'>Submit Rating</Button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}


/*
{test_metric_names.map((metric, index) => (
    <div key={index}>
        <label>Slider: {metric}</label>
        <div>
            <input type="range" min="1" max="5" value="3" id={metric}></input>
        </div>
    </div>
))}
*/