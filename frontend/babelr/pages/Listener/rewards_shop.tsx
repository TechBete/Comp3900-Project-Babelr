import styles from "stylesheets/rewards_shop.module.css";
import Navbar_Listener from "components/nav_bar_listener";
import { useState } from "react";
import { Button } from "@mui/material";
import RoleCheck from "components/role_checker";

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
                return 
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
          <img src={reward.logo} alt={reward.title} className={styles.rewardImage}/>
          <h2 className={styles.rewardTitle}>{reward.title}</h2>
          <h4 className={styles.rewardCost}>{reward.cost} Points</h4>
          <Button className={styles.button} onClick={() => Redeem(reward.title)}>Redeem</Button>
        </div>
    ));
    
    return (
        <RoleCheck requiredRole="listener">
            <div className={styles.pageWrapper}>
                <Navbar_Listener></Navbar_Listener>
                <div className={styles["second_bar"]}>
                    <h1 className={styles.header}>Rewards Shop</h1>
                    <p className={styles.subText}>Redeem your reward below</p>
                </div>
                <div className={styles["container"]}>
                    <div className={styles.rewardsGrid}>
                    {reward_grid}
                    </div>
                </div>
            </div>
        </RoleCheck>
    );
}