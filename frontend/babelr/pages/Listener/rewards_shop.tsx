import styles from "stylesheets/rewards_shop.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import { useState } from "react";
import Image from "next/image";
import { Button } from "@mui/material";

export default function Rewards_shop() {
    const [Error, setError] = useState("");

    async function Redeem(id: number) {
        try {
            const response = await fetch(`http://localhost:8016/listener/redeemRewards}`, {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'reward_id': id}),
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

    const test_reward_list = [
        {'id': 1, 'img': 'l', 'title': 'Woolworths', 'cost': 20},
        {'id': 2, 'img': 'g', 'title': 'Coles', 'cost': 50},
    ];

    const reward_grid = test_reward_list.map((reward) => (
        <div key={reward.id} className="w-45 h-45 bg-gray-200 p-2 flex flex-col items-center justify-between rounded-lg shadow-md">
          <Image src='/babelr_icon.png' alt={reward.title} className="w-20 h-20 object-cover rounded-md" />
          <h2 className="text-center text-sm font-medium">{reward.title}</h2>
          <h4 className="text-center text-sm font-medium">{reward.cost} Points</h4>
          <Button variant="contained" onClick={() => Redeem(reward.id)}>Redeem</Button>
        </div>
    ));

    return (
        <div>
            <Navbar_Listener></Navbar_Listener>
            <div className={styles["second_bar"]}>
                <h1 className="">Rewards Shop</h1>
                <p></p>
                <p></p>
                <p>Please redeem information below.</p>
            </div>
            <div className={styles["container"]}>
                {reward_grid}
            </div>
        </div>
    );
}