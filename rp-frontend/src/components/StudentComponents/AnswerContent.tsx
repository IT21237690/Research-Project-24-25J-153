import React, { useEffect, useState } from "react";

const AnswerContent = () => {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [question, setQuestion] = useState<string | null>(null);
  const [userAnswer, setUserAnswer] = useState<string>("");
  // Fetch passage from localStorage
  const [passage, setPassage] = useState<string>(localStorage.getItem("passage") || "passage");

  useEffect(() => {
    const handleStorageUpdate = () => {
      setPassage(localStorage.getItem("passage") || "passage");
    };
  
    // Listen for passage updates from other components
    window.addEventListener("passageUpdated", handleStorageUpdate);
  
    return () => {
      window.removeEventListener("passageUpdated", handleStorageUpdate);
    };
  }, []);  console.log("passage in answer", passage);
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
        method: "POST", // POST method as we are sending data in the request body
        headers: {
          "Content-Type": "application/json", // Content type set to JSON
          Accept: "application/json", // Accept response as JSON
        },
        body: JSON.stringify(requestBody), // Send passage and question type as the body
      });

      if (!response.ok) {
        throw new Error("Failed to generate question");
      }

      const data = await response.json(); // Parse the response to JSON
      if (data && data.generated_question) {
        setQuestion(data.generated_question); // Set the generated question in the state
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
    const fullPassage = localStorage.getItem("passage") || "Default passage";  // Full passage from localStorage
    const currentDifficulty = localStorage.getItem("current_difficulty") || "50";  // Difficulty from localStorage
  
    if (!selectedType || !question || !userAnswer) {
      console.error("Missing required fields for API request.");
      return;
    }
  
    // Extract first sentence only if the question type is JSQ
    const passageToSend = selectedType === "JSQ" ? extractFirstSentence(fullPassage) : fullPassage;
  
    const requestBody = {
      current_difficulty: Number(currentDifficulty),
      user_answer: userAnswer,
      passage: passageToSend,  // Use the extracted passage here
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
        localStorage.setItem("difficultyScore", String(data.updated_difficulty));
        console.log("Updated difficulty saved:", data.updated_difficulty);
      }
  
    } catch (error) {
      console.error("Error calling adjust_difficulty API:", error);
    }
  };
  
  const renderStars = () => {
    if (reward === null) return null;

    const handleNext = () => {
        // Reload the page to fetch a new passage
        window.location.reload();
    };

    return (
      <div className="flex flex-col items-center bg-white rounded-lg shadow-md p-6 mt-5">
        <h2 className="text-lg font-bold">Your Answer vs Correct Answer</h2>
        <p className="text-gray-700 mt-2"><strong>Your Answer:</strong> {userAnswer}</p>
        <p className="text-gray-700"><strong>Correct Answer:</strong> {correctAnswer}</p>

        <div className="flex space-x-2 text-4xl mt-4">
          <span className={reward === -1 ? "text-yellow-400" : "text-gray-300"}>⭐</span>
          <span className={reward >= 0 ? "text-yellow-400" : "text-gray-300"}>⭐</span>
          <span className={reward === 1 ? "text-yellow-400" : "text-gray-300"}>⭐</span>
        </div>

        <p className="text-lg font-semibold mt-3">
          {reward === -1 ? "Nice try! Keep practicing!" : reward === 0 ? "Good job! Almost there!" : "Excellent! Well done!"}
        </p>

        <button
          onClick={handleNext}
          className="mt-4 bg-green-500 text-white font-semibold py-3 px-6 rounded-md shadow-md hover:bg-green-600 transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-2"
        >
          Next
        </button>
      </div>
    );
};

  
  return (
    <div className="bg-white rounded-lg shadow-md p-5 w-full max-w-none mt-5">
      {reward === null ? (
        !selectedType ? (
          <div className="flex justify-center gap-4">
            <button onClick={() => handleQuestionType("SAQ")} className="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600">
              Short Answer Question ?
            </button>
            <button onClick={() => handleQuestionType("JSQ")} className="bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600">
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
            <button
              onClick={handleSubmit}
              className="mt-4 w-full bg-blue-500 text-white font-semibold py-3 rounded-md shadow-md hover:bg-blue-600 transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
            >
              Submit
            </button>
          </>
        )
      ) : (
        renderStars()
      )}
    </div>
  );
};

export default AnswerContent;
