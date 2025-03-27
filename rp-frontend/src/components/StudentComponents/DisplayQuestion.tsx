import React, { useState, useEffect } from "react";

const DisplayQuestion = () => {
  const [passage, setPassage] = useState<string>(""); // Change to store the passage as a string
  // Retrieve stored values from localStorage
  const grade = localStorage.getItem("grade") || "1"; // Default to grade 1 if not found
  const difficulty = localStorage.getItem("qnadifficultyScore") || "5"; // Default difficulty 5 if not found

  const [loading, setLoading] = useState<boolean>(true); // State to handle loading state
  const [error, setError] = useState<string | null>(null); // S
  const passageAPI = `http://localhost:8004/retrieve_passage/${difficulty}/${grade}`;
  useEffect(() => {
    const fetchPassage = async () => {
      setLoading(true);
      setError(null);
      // setReadingDifficulty(difficulty);
      try {
        const response = await fetch(passageAPI, {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
          // throw new Error("Failed to fetch passage");
        }

        const data = await response.json();
        if (data?.passage) {
          setPassage(data.passage);

          localStorage.setItem("qnapassage", data.passage);
          window.dispatchEvent(new Event("passageUpdated"));
        } else {
          // setError("No passage data available");
        }
      } catch (error) {
        setError(error.message || "An unknown error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchPassage();
  }, [difficulty, grade]);

  // console.log("passage in question", localStorage.passage)

  return (
    <div className="bg-white/30 text-black rounded-lg shadow-md p-5 mt-9 w-full max-w-none text-center backdrop-blur-lg">
      <h2 className="text-5xl font-bold mb-3 text-pink-500">
        Read the Passage
      </h2>

      {loading && (
        <div className="flex items-center justify-center">
          <svg
            className="animate-spin h-12 w-12 text-blue-500"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v4l5-5-5-5v4a4 4 0 00-4 4z"
            ></path>
          </svg>
          <p className="ml-4 text-lg font-semibold text-teal-500 animate-pulse">
            Loading Passage...
          </p>
        </div>
      )}
      {error && <p className="text-red-500">{error}</p>}

      <p className="text-black text-3xl font-bold">
        {passage ? passage : "No passage available"}
      </p>
    </div>
  );
};

export default DisplayQuestion;
