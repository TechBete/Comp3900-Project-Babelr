// import { FormEvent, useState } from "react";
import styles from "stylesheets/first_time_listener.module.css";
import Image from "next/image";


export default function Rewards_shop() {
    return (
            <div className={styles["body"]}>
                <div className={styles["form-container"]}>
                    <div className={styles["information-container"]}>
                        <div className={styles["header-wrapper"]}>
                            <h1>Rewards Shop</h1>
                            <p>Please redeem information below.</p>
                        </div>
                    </div>
                </div>
                <div className={styles["image-container"]}>
                    <Image src="/babelr_logo.png" alt="side-image" width={1024} height={1024}/>
                </div>
            </div>
    );
}   