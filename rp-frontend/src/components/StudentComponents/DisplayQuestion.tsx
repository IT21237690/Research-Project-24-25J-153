import React, { useState, useEffect } from "react";

const DisplayQuestion = () => {
    const [passage, setPassage] = useState<string>(""); // Change to store the passage as a string
    // Retrieve stored values from localStorage
  const grade = localStorage.getItem("grade") || "1"; // Default to grade 1 if not found
  const difficulty = localStorage.getItem("difficultyScore") || "5"; // Default difficulty 5 if not found
  const [loading, setLoading] = useState<boolean>(true); // State to handle loading state
  const [error, setError] = useState<string | null>(null); // S
  const passageAPI = `http://localhost:8004/retrieve_passage/${difficulty}/${grade}`;
  useEffect(() => {
    const fetchPassage = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(passageAPI, {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch passage");
        }

        const data = await response.json();
        if (data?.passage) {
          setPassage(data.passage);

          localStorage.setItem("passage", data.passage);
          window.dispatchEvent(new Event("passageUpdated")); 
        } else {
          setError("No passage data available");
        }
      } catch (error) {
        setError(error.message || "An unknown error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchPassage();
  }, [difficulty, grade]); 
 
  console.log("passage in question", localStorage.passage)

  return (
    <div className="bg-white text-black rounded-lg shadow-md p-5 mt-9 w-full max-w-none text-center">
      <h2 className="text-xl font-bold mb-3">Read the Passage</h2>

      {loading && <p className="text-gray-200">Loading passage...</p>}
      {error && <p className="text-red-500">{error}</p>}

      <p className="text-black">
        {passage ? passage : "No passage available"}
      </p>
    </div>
  );
};


export default DisplayQuestion;
