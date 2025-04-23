import styles from "stylesheets/rewards_shop.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import { useState } from "react";
import Image from "next/image";
import { Button } from "@mui/material";

export default function Rewards_shop() {
    const [Error, setError] = useState("");

    async function Redeem(name: string) {
        try {
            const response = await fetch(`http://localhost:8016/listener/redeemRewards`, {
                method:"POST",
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'redeem_name': name, 'point': 4}),
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
        {'id': 1, 'img': 'l', 'title': 'Woolworths', 'cost': 20, 'logo': '/woolworths_logo.png'},
        {'id': 2, 'img': 'g', 'title': 'Coles', 'cost': 50, 'logo': '/coles_logo.png'},
    ];

    const reward_grid = test_reward_list.map((reward) => (
        <div key={reward.id} className="w-45 h-45 bg-gray-200 p-2 flex flex-col items-center justify-between rounded-lg shadow-md">
          <Image src={reward.logo} alt={reward.title} className="w-20 h-20 object-cover rounded-md" />
          <h2 className="text-center text-sm font-medium">{reward.title}</h2>
          <h4 className="text-center text-sm font-medium">{reward.cost} Points</h4>
          <Button 
            sx={{
            backgroundColor: "#2b4450",
            "&:hover": {
                backgroundColor: "#1f333c",
            },
            }}  
            variant="contained" 
            onClick={() => Redeem(reward.title)}>Redeem</Button>
        </div>
    ));

    return (
        <div className={styles.pageWrapper}>
            <Navbar_Listener></Navbar_Listener>
            <div className={styles["second_bar"]}>
                <h1 className="text-3xl font-bold text-center mb-4">Rewards Shop</h1>
                <p className=" text-center">Redeem your reward below</p>
            </div>
            <div className={styles["container"]}>
                <div className="grid grid-cols-2 gap-40">
                {reward_grid}
                </div>
            </div>
        </div>
    );
}