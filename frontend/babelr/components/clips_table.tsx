import React from "react";
import styles from "stylesheets/clips_table.module.css";

const AudioClipsTable = () => {
  const audioClips = [
    {
      name: "Screaming.mp3",
      tags: ["Fast Speech", "Child"],
      dateAdded: "2/5/2025",
      evaluated: "48/50",
      rating: "3.6",
    },
    {
      name: "A song.wav",
      tags: ["Style Speech", "Adult"],
      dateAdded: "5/4/2025",
      evaluated: "90/50",
      rating: "2.375",
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>Audio Clips</h2>
        <input type="text" placeholder="Search" className={styles.search} />
        <button className={styles.advancedSearch}>Advanced Search ▼</button>
      </div>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Audio Clips</th>
            <th>Tags</th>
            <th>Date Added</th>
            <th>Evaluated</th>
            <th>Rating</th>
          </tr>
        </thead>
        <tbody>
          {audioClips.map((clip, index) => (
            <tr key={index}>
              <td>
                <a href="#" className={styles.audioLink}>{clip.name}</a>
              </td>
              <td>
                {clip.tags.map((tag, i) => (
                  <span key={i} className={styles.tag}>{tag}</span>
                ))}
              </td>
              <td>{clip.dateAdded}</td>
              <td>{clip.evaluated}</td>
              <td>{clip.rating}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AudioClipsTable;