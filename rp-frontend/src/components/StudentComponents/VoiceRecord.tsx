import React, { useState, useRef } from "react";

const VoiceRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Start Recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioBlob(audioBlob);
        setAudioUrl(audioUrl);
        audioChunksRef.current = []; // Clear chunks
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  // Stop Recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Send the recorded audio (Replace with actual API call)
  const sendAudio = () => {
    if (!audioBlob) return;
    const formData = new FormData();
    formData.append("audio", audioBlob, "student-recording.webm");

    console.log("Audio ready to be sent!");
    // Example API call: fetch("your-api-url", { method: "POST", body: formData })
  };

  return (
    <div className="flex flex-col items-center p-4 bg-white shadow-md rounded-lg w-full">
      <h2 className="text-xl font-bold mb-4">Record Your Voice</h2>
      
      {/* Record Button */}
      {!isRecording ? (
        <button 
          onClick={startRecording} 
          className="bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600"
        >
          🎤 Start Recording
        </button>
      ) : (
        <button 
          onClick={stopRecording} 
          className="bg-red-500 text-white px-6 py-2 rounded-md hover:bg-red-600"
        >
          ⏹ Stop Recording
        </button>
      )}

      {/* Playback and Send */}
      {audioUrl && (
        <div className="mt-4 flex flex-col items-center">
          <audio controls src={audioUrl} className="mb-2 w-full"></audio>
          <button 
            onClick={sendAudio} 
            className="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600"
          >
            📤 Send Recording
          </button>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;
