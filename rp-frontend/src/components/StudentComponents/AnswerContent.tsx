import React, { useEffect, useState } from "react";
import { FaStar } from "react-icons/fa";

const AnswerContent = () => {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [question, setQuestion] = useState<string | null>(null);
  const [userAnswer, setUserAnswer] = useState<string>("");
  // Fetch passage from localStorage
  const [passage, setPassage] = useState<string>(
    localStorage.getItem("qnapassage") || "qnapassage"
  );

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
    const url = "http://127.0.0.1:8001/generate_question/";

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
  const [correctAnswer, setCorrectAnswer] = useState<string | null>(null);

  const handleSubmit = async () => {
    const fullPassage = localStorage.getItem("qnapassage") || "Default passage"; // Full passage from localStorage
    const currentDifficulty =
      localStorage.getItem("qnacurrent_difficulty") || "50"; // Difficulty from localStorage

    if (!selectedType || !question || !userAnswer) {
      console.error("Missing required fields for API request.");
      return;
    }

    // Extract first sentence only if the question type is JSQ
    const passageToSend =
      selectedType === "JSQ" ? extractFirstSentence(fullPassage) : fullPassage;

    const requestBody = {
      current_difficulty: Number(currentDifficulty),
      user_answer: userAnswer,
      passage: passageToSend, // Use the extracted passage here
      question: question,
      question_type: selectedType,
    };

    try {
      const response = await fetch(
        "http://127.0.0.1:8003/adjust_difficulty/67d54d44f327fe819f298c1c/5",
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
      setCorrectAnswer(data.gold_answer || "No correct answer provided");

      if (data.updated_difficulty !== undefined) {
        localStorage.setItem(
          "qnadifficultyScore",
          String(data.updated_difficulty)
        );
        // console.log("Updated difficulty saved:", data.updated_difficulty);
      }
    } catch (error) {
      console.error("Error calling adjust_difficulty API:", error);
    }
  };

  const renderStars = (reward) => {
    if (reward === null) return null;

    const handleNext = () => {
      // Reload the page to fetch a new passage
      window.location.reload();
    };

    return (
<div className="flex flex-col items-center bg-white/30 text-white rounded-lg shadow-md p-6 mt-5 backdrop-blur-lg">
  <h2 className="text-2xl font-extrabold text-pink-400">Your Answer and Correct Answer</h2>
  
  <p className="text-gray-900 mt-4 text-xl font-semibold">
    <strong>Your Answer:</strong> {userAnswer}
  </p>
  <p className="text-gray-900 text-xl font-semibold">
    <strong>Correct Answer:</strong> {correctAnswer}
  </p>

  <div className="flex space-x-2 text-5xl mt-6">
    {reward === -1 ? (
      <FaStar className="text-yellow-300 text-5xl">⭐</FaStar>
    ) : reward === 0 ? (
      <FaStar className="text-yellow-400 text-5xl">⭐⭐</FaStar>
    ) : (
      <FaStar className="text-yellow-500 text-5xl">⭐⭐⭐</FaStar>
    )}
  </div>

  <p className="text-xl font-bold mt-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-pink-400 animate-gradient-text hover:scale-105 transition-all duration- text-5xl">
  {reward === -1
      ? "Nice try! Keep practicing!"
      : reward === 0
      ? "Good job! Almost there!"
      : "Excellent! Well done!"}
  </p>

  <button
    onClick={handleNext}
    className="mt-6 bg-gradient-to-r from-pink-400 via-pink-500 to-pink-600 text-white text-xl font-bold py-4 px-8 rounded-lg shadow-xl hover:scale-110 transform transition duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-pink-300 focus:ring-offset-2"
  >
    Next
  </button>
</div>

    );
  };

  return (
    <div className="bg-white/30 rounded-lg shadow-md p-5 w-full max-w-none mt-5 backdrop-blur-lg">
      {reward === null ? (
        !selectedType ? (
          <div className="flex justify-center gap-4">
            <button
              onClick={() => handleQuestionType("SAQ")}
              className="bg-gradient-to-r from-purple-400 via-pink-500 to-red-500 text-white text-xl font-semibold px-8 py-4 rounded-lg shadow-lg transform transition-all duration-300 hover:scale-105 hover:from-pink-500 hover:to-yellow-500 hover:shadow-2xl focus:outline-none"
            >
              Short Answer Question ?
            </button>
            <button
              onClick={() => handleQuestionType("JSQ")}
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
                onClick={handleSubmit}
                className="w-48 bg-gradient-to-r from-teal-400 via-blue-500 to-purple-600 text-white text-2xl font-bold py-3 rounded-md shadow-lg hover:scale-105 transition duration-300 ease-in-out transform hover:from-purple-600 hover:to-teal-400 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
              >
                Submit
              </button>
            </div>
          </>
        )
      ) : (
        renderStars(reward)
      )}
    </div>
  );
};

export default AnswerContent;
