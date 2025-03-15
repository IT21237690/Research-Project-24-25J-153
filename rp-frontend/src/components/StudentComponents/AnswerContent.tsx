import React, { useState } from "react";

const AnswerContent = () => {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [question, setQuestion] = useState<string | null>(null);
  const [userAnswer, setUserAnswer] = useState<string>("");
  // Fetch passage from localStorage
  const passage = localStorage.getItem("passage") || "passage"; 
  console.log("passage in answer", passage)

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
          "Accept": "application/json", // Accept response as JSON
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
    setSelectedType(type); // Update the question type (first)
    if (passage) {
      // Immediately generate the question after updating the type
      generateQuestion(passage, type);
    } else {
      console.error("No passage available in localStorage");
    }
  };
  return (
    <div className="bg-white rounded-lg shadow-md p-5 w-full max-w-none mt-5">
      {!selectedType ? (
        <div className="flex justify-center gap-4">
          <button
            onClick={() => handleQuestionType("SAQ")}
            className="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600"
          >
            Short Answer Question ?
          </button>
          <button
            onClick={() => handleQuestionType("JSQ")}
            className="bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600"
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
        </>
      )}
    </div>
  );
};

export default AnswerContent;
