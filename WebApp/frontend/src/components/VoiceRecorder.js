import React, { useState, useRef } from "react";

const VoiceRecorder = ({ sentence, onFeedback }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const recorderRef = useRef(null); // Use useRef to store the recorder instance

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const localChunks = [];
      recorderRef.current = recorder; // Store the recorder instance in the ref

      recorder.ondataavailable = (event) => {
        localChunks.push(event.data);
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(localChunks, { type: "audio/wav" });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);

        const formData = new FormData();
        formData.append("audio", audioBlob);
        formData.append("sentence", sentence);

        try {
          const response = await fetch("http://localhost:5000/analyze", {
            method: "POST",
            body: formData,
          });
          const feedback = await response.json();
          onFeedback(feedback);
        } catch (error) {
          console.error("Error sending audio:", error);
        }
      };

      recorder.start();
      setIsRecording(true);

     
    } catch (err) {
      console.error("Error accessing microphone:", err);
    }
  };

  const stopRecording = async()=>{
    recorderRef.current.stop();
          setIsRecording(false);
  }

  return (
    <div>
      <button onClick={startRecording} disabled={isRecording}>
        Start Recording
      </button>
      <button onClick={stopRecording} >
        Stop Recording
      </button>

      {audioUrl && (
        <div>
          <h3>Playback:</h3>
          <audio controls src={audioUrl}></audio>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;
