import React, { useState, useRef, useEffect } from "react";
import { FaMicrophone } from "react-icons/fa";
import GetStars from "./GetStars.tsx";
import { useSound } from "../../context/Sound.context.tsx";
import LoadingComponent from "./LoadingComponent.tsx";

const VoiceAnswerContent = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [passage, setPassage] = useState<string>(
    localStorage.getItem("fnppassage") || "fnppassage"
  );
  console.log(passage, "inside answer content");
  const [fluencyScore, setFluencyScore] = useState<number>(0);
  const [pronunciationScore, setPronunciationScore] = useState<number>(0);
  const [mispronouncedWords, setMispronouncedWords] = useState<string[]>([]);
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
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/wav", // Make sure the type is set to 'audio/wav'
        });
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
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<string | null>(null);
  const difficulty = localStorage.getItem("fnpdifficultyScore") || "5"; // Default difficulty 5 if not found
  const userId = localStorage.getItem("userId") || "5"; // Default difficulty 5 if not found
  useEffect(() => {
    const updatePassage = () => {
      const newPassage = localStorage.getItem("fnppassage") || "fnppassage";
      setPassage(newPassage);
      console.log("Passage updated in VoiceAnswerContent:", newPassage);
    };

    // Listen for passage updates
    window.addEventListener("passageUpdated", updatePassage);

    // Cleanup listener when component unmounts
    return () => {
      window.removeEventListener("passageUpdated", updatePassage);
    };
  }, []);
  // Send the recorded audio and passage text to the API
  const sendAudio = async () => {
    // Ensure there is an audioBlob and a passage text
    if (!audioBlob || !passage) {
      alert("Please record the audio and provide the passage text.");
      return;
    }

    // Show the loading state
    setIsLoading(true);
    setResponse(null); // Clear previous response messages

    const formData = new FormData();
    formData.append("file", audioBlob, "student-recording.wav"); // Attach the recorded audio as 'file'
    formData.append("reference_text", passage); // Attach the passage text
    console.log(passage, "before analyze");

    try {
      // Replace with your actual API endpoint
      const response = await fetch(`http://localhost:7000/${userId}/analyze`, {
        method: "POST",
        body: formData,
      });

      // Check if the response is OK
      if (response.ok) {
        const data = await response.json();
        // Extracting and setting state from the response data
        setFluencyScore(data.final_fuency_score);
        setPronunciationScore(data.pronunciation_score);
        setMispronouncedWords(data.mispronounced_words);
        console.log("data fluency", data.final_fuency_score);
        setResponse(data);
      } else {
        console.error("Failed to send audio and passage.");
        setResponse("Sorry, something went wrong. Please try again.");
      }
    } catch (error) {
      console.error("Error sending audio and passage:", error);
      setResponse(
        "Error sending audio. Please check your connection and try again."
      );
    } finally {
      // Hide the loading state
      setIsLoading(false);
    }
  };
  console.log("data setfluency", fluencyScore);

  const updateScore = async (fluencyScore, difficulty, userId) => {
    console.log("data use api fluency", fluencyScore);

    const url = `http://localhost:8003/update_score/${userId}/${fluencyScore}/${difficulty}`;

    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("fnpdifficultyScore", data.updated_score);
      } else {
        console.error("Error updating score:", response.status);
      }
    } catch (error) {
      console.error("Request failed", error);
    }
  };
  const handleNext = async () => {
    await updateScore(fluencyScore, difficulty, userId);
    window.location.reload();
  };
  const { soundEnabled } = useSound();
  const soundRef = useRef<HTMLAudioElement>(null); // Create a ref to the audio element
  const submitSoundRef = useRef<HTMLAudioElement>(null); // Create a ref to the audio element

  const handleButtonClick = () => {
    if (soundEnabled && soundRef.current) {
      soundRef.current
        .play()
        .catch((err) => console.warn("Button sound failed:", err));
    }
  };

  const handleSubmitSoundClick = () => {
    if (soundEnabled && submitSoundRef.current) {
      submitSoundRef.current
        .play()
        .catch((err) => console.warn("Submit sound failed:", err));
    }
  };

  return (
    <div className="bg-white/30 rounded-lg shadow-md p-5 w-full max-w-none mt-5 backdrop-blur-lg">
      <audio ref={soundRef} src="/sounds/recordClick.mp3" preload="auto" />
      <audio
        ref={submitSoundRef}
        src="/sounds/generalButtonClick.mp3"
        preload="auto"
      />

      {/* Only show the recording UI if not loading or showing a response */}
      {!isLoading && !response && (
        <div className="flex flex-col items-center p-4 bg-white/30 shadow-md rounded-lg w-full backdrop-blur-lg">
          <h2 className="text-3xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-pink-400 via-blue-400 to-purple-400">
            Let's Record Your Reading
          </h2>

          {/* Record Button */}
          {!isRecording ? (
            <div className="flex flex-col items-center space-y-2">
              <button
                // onClick={startRecording}
                onClick={() => {
                  handleButtonClick(); // Play sound on click
                  startRecording();
                }}
                className="bg-gradient-to-r from-pink-400 via-blue-400 to-purple-400 p-6 rounded-full hover:scale-110 transform transition-all duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-pink-300 focus:ring-offset-2"
              >
                <FaMicrophone className="text-white text-6xl animate-pulse" />
              </button>
            </div>
          ) : (
            <>
              <button
                // onClick={stopRecording}
                onClick={() => {
                  handleButtonClick(); // Play sound on click
                  stopRecording();
                }}
                className="bg-gradient-to-r from-green-400 via-yellow-400 to-red-400 p-6 rounded-full hover:scale-110 transform transition-all duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-green-300 focus:ring-offset-2"
              >
                <FaMicrophone className="text-white text-6xl" />
              </button>
              <p className="text-lg font-semibold text-black mt-3">
                {isRecording
                  ? "Click me when you're done"
                  : "Click me to start recording"}
              </p>
            </>
          )}

          {/* Show audio controls and send button after recording */}
          {audioUrl && !isLoading && (
            <div className="mt-4 flex flex-col items-center">
              <audio controls src={audioUrl} className="mb-2 w-full"></audio>
              <button
                onClick={() => {
                  handleSubmitSoundClick(); // Play sound on click
                  sendAudio();
                }}
                className="bg-gradient-to-r from-blue-400 via-indigo-500 to-purple-500 text-white px-8 py-4 rounded-full text-xl font-bold hover:scale-110 transform transition-all duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-offset-2 flex items-center space-x-2"
              >
                <span>📤</span>
                <span>Send Your Recording</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Loading Animation and Message */}
      {isLoading && (
        <LoadingComponent isLoading={isLoading} />

      )}

      {/* Response with Fluency, Pronunciation, and Mispronounced Words */}
      {response && !isLoading && (
        <div className="mt-6 text-center">
          {/* Fluency Score */}
          {fluencyScore !== null && (
            <div className="mb-4">
              <p className="text-lg font-semibold">Fluency</p>
              <GetStars score={fluencyScore} color="yellow" />
            </div>
          )}

          {/* Pronunciation Score */}
          {pronunciationScore !== null && (
            <div className="mb-4">
              <p className="text-lg font-semibold">Pronunciation</p>
              <GetStars score={pronunciationScore} color="green" />
            </div>
          )}
          {/* Mispronounced Words */}
          {mispronouncedWords.length > 0 && (
            <div className="mb-4">
              <p className="text-lg font-semibold">Mispronounced Words:</p>
              <p className="text-md font-medium text-gray-700">
                {mispronouncedWords.join(", ")}
              </p>
            </div>
          )}

          {/* Next Button */}
          <div className="mt-4">
            <button
              onClick={() => {
                handleSubmitSoundClick(); // Play sound on click
                handleNext();
              }}
              className="bg-gradient-to-r from-blue-400 via-indigo-500 to-purple-500 text-white px-8 py-4 rounded-full text-xl font-bold hover:scale-110 transform transition-all duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-offset-2"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceAnswerContent;
