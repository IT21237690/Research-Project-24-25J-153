import React, { useEffect, useRef, useState } from "react";
import RenderStars from "./RenderStars.tsx";
import { useSound } from "../../context/Sound.context.tsx";

const AnswerContent = () => {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [question, setQuestion] = useState<string | null>(null);
  const [userAnswer, setUserAnswer] = useState<string>("");
  // Fetch passage from localStorage
  const [passage, setPassage] = useState<string>(
    localStorage.getItem("qnapassage") || "qnapassage"
  );
  const userId = localStorage.getItem("userId") || "5"; // Default difficulty 5 if not found
  const grade = localStorage.getItem("grade") || "5"; // Default difficulty 5 if not found

  console.log("PASSAGE RETRIVAL USER ID", userId);
  useEffect(() => {
    const handleStorageUpdate = () => {
      setPassage(localStorage.getItem("qnapassage") || "qnapassage");
    };

    // Listen for passage updates from other components
    window.addEventListener("passageUpdated", handleStorageUpdate);

    return () => {
      window.removeEventListener("passageUpdated", handleStorageUpdate);
    };
  }, []);
  // console.log("passage in answer", passage);
  const extractFirstSentence = (text: string): string => {
    const sentences = text.match(/[^.!?]+[.!?]/g); // Split text into sentences
    return sentences ? sentences[0] : text; // Return first sentence or full passage if not split
  };
  const generateQuestion = async (passage: string, questionType: string) => {
    const url = "http://20.193.146.113:8001/generate_question/";

    const requestBody = {
      passage: passage,
      question_type: questionType,
    };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error("Failed to generate question");
      }

      const data = await response.json();
      if (data && data.generated_question) {
        setQuestion(data.generated_question);
      } else {
        console.error("Error: No question in response");
      }
    } catch (error) {
      console.error("Error calling generate_question API:", error);
    }
  };

  const handleQuestionType = (type: string) => {
    setSelectedType(type);
    if (passage) {
      const textToSend =
        type === "JSQ" ? extractFirstSentence(passage) : passage;
      generateQuestion(textToSend, type);
    } else {
      console.error("No passage available in localStorage");
    }
  };
  const [reward, setReward] = useState<number | null>(null);
  const [similarity, setSimilarity] = useState<number | null>(null);

  const [correctAnswer, setCorrectAnswer] = useState<string | null>(null);

  const handleSubmit = async () => {
    const fullPassage = localStorage.getItem("qnapassage") || "Default passage"; // Full passage from localStorage
    const currentDifficulty =
      localStorage.getItem("qnadifficultyScore") || "50"; // Difficulty from localStorage

    if (!selectedType || !question || !userAnswer) {
      console.error("Missing required fields for API request.");
      return;
    }

    // Extract first sentence only if the question type is JSQ
    const passageToSend =
      selectedType === "JSQ" ? extractFirstSentence(fullPassage) : fullPassage;

    const requestBody = {
      current_difficulty: Math.round(Number(currentDifficulty)), // Convert to integer
      user_answer: userAnswer,
      passage: passageToSend, // Use the extracted passage here
      question: question,
      question_type: selectedType,
    };

    try {
      const response = await fetch(
        `http://20.193.146.113:8003/adjust_difficulty/${userId}/${grade}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to adjust difficulty");
      }

      const data = await response.json();

      setReward(data.reward);
      setSimilarity(data.similarity);
      setCorrectAnswer(data.gold_answer || "No correct answer provided");

      if (data.updated_difficulty !== undefined) {
        localStorage.setItem(
          "qnadifficultyScore",
          String(data.updated_difficulty)
        );
        console.log("Updated difficulty saved:", data.updated_difficulty);
      }
    } catch (error) {
      console.error("Error calling adjust_difficulty API:", error);
    }
  };

  const soundRef = useRef<HTMLAudioElement>(null); // Create a ref to the audio element
  const { soundEnabled } = useSound();

  const handleButtonClick = () => {
    if (soundEnabled && soundRef.current) {
      soundRef.current.play().catch((err) => {
        console.warn("Audio playback failed:", err);
      });
    }
  };

  return (
    <div className="bg-white/30 rounded-lg shadow-md p-5 w-full max-w-none mt-5 backdrop-blur-lg">
      <audio ref={soundRef} src="/sounds/generalButtonClick.mp3" preload="auto" />

      {reward === null ? (
        !selectedType ? (
          <div className="flex justify-center gap-4">
            <button
              onClick={() => {
                handleButtonClick(); // Play sound on click
                handleQuestionType("SAQ");
              }}
              className="bg-gradient-to-r from-purple-400 via-pink-500 to-red-500 text-white text-xl font-semibold px-8 py-4 rounded-lg shadow-lg transform transition-all duration-300 hover:scale-105 hover:from-pink-500 hover:to-yellow-500 hover:shadow-2xl focus:outline-none"
            >
              Short Answer Question ?
            </button>
            <button
              onClick={() => {
                handleButtonClick(); // Play sound on click
                handleQuestionType("JSQ");
              }}
              className="bg-gradient-to-r from-teal-400 via-green-500 to-yellow-400 text-white text-xl font-semibold px-8 py-4 rounded-lg shadow-lg transform transition-all duration-300 hover:scale-105 hover:from-green-500 hover:to-blue-500 hover:shadow-2xl focus:outline-none"
            >
              Jumble Sentence Question?
            </button>
          </div>
        ) : (
          <>
            <h2 className="text-lg font-bold mb-3">Question:</h2>
            <p className="text-gray-700">{question || "Loading question..."}</p>
            <input
              type="text"
              placeholder="Enter your answer here..."
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              className="w-full mt-3 p-3 border border-gray-400 rounded-md"
            />
            <div className="flex justify-center items-center mt-4">
              <button
                onClick={() => {
                  handleButtonClick(); // Play sound on click
                  handleSubmit();
                }}
                className="w-48 bg-gradient-to-r from-teal-400 via-blue-500 to-purple-600 text-white text-2xl font-bold py-3 rounded-md shadow-lg hover:scale-105 transition duration-300 ease-in-out transform hover:from-purple-600 hover:to-teal-400 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
              >
                Submit
              </button>
            </div>
          </>
        )
      ) : (
        // renderStars(similarity)
        <div>
          <RenderStars
            similarity={similarity}
            userAnswer={userAnswer}
            correctAnswer={correctAnswer}
          />
        </div>
      )}
    </div>
  );
};

export default AnswerContent;
