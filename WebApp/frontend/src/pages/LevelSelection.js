import React, { useState } from "react";
import VoiceRecorder from "../components/VoiceRecorder";

function LevelSelection() {
  const [level, setLevel] = useState("");
  const [sentence, setSentence] = useState("");
  const fetchSentence = async (level) => {
    try {
      const response = await fetch(
        `http://localhost:5000/sentence?level=${level}`
      );
      const data = await response.json();
      setSentence(data.sentence);
    } catch (error) {
      console.error("Error fetching sentence:", error);
    }
  };

  const handleLevelChange = (selectedLevel) => {
    setLevel(selectedLevel);
    fetchSentence(selectedLevel);
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Choose a Level</h1>
      <div>
        <button onClick={() => handleLevelChange("beginner")}>Beginner</button>
        <button onClick={() => handleLevelChange("intermediate")}>
          Intermediate
        </button>
        <button onClick={() => handleLevelChange("advanced")}>Advanced</button>
      </div>
      <div style={{ marginTop: "20px" }}>
        <h2>
          Selected Level: {level.charAt(0).toUpperCase() + level.slice(1)}
        </h2>
        <p>
          <strong>Sentence:</strong> {sentence || "No sentence yet."}
        </p>
      </div>
      <VoiceRecorder 
  sentence={sentence} 
  onFeedback={(feedback) => console.log('Feedback:', feedback)} 
/>
    </div>
  );
}
export default LevelSelection;
