import React, { useState, useEffect } from "react";
import { IoChevronDown, IoChevronUp } from "react-icons/io5";
import ResultsTable from "./ResultsTable.tsx";

const token = localStorage.getItem("token");
const API_URL = "http://20.193.146.113:5000/api/users/results";

const ResultContent = () => {
  const [expandedSection, setExpandedSection] = useState(null);
  const [qaData, setQaData] = useState([]);
  const [pronunciationData, setPronunciationData] = useState([]);
  const [loading, setLoading] = useState(true);
  console.log("TOKEN PASED", token)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(API_URL, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) throw new Error("Failed to fetch data");

        const result = await response.json();
        setQaData(result.results.QA || []);
        setPronunciationData(result.results.pronunciation || []);
      } catch (error) {
        console.error("Error fetching results:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, []);

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="bg-white/30 rounded-lg shadow-md p-5 w-full mt-5 backdrop-blur-lg">
      {[
        "Reading Passages",
        "Question Answering",
        "Vocabulary Building",
        "Image Description",
      ].map((section, index) => (
        <div key={index} className="w-full">
          <button
            className="w-full flex justify-between items-center bg-gradient-to-r from-blue-400 to-pink-400 text-white p-4 rounded-lg mb-2 text-xl font-bold transition-all"
            onClick={() => toggleSection(section)}
          >
            {section}
            {expandedSection === section ? <IoChevronUp /> : <IoChevronDown />}
          </button>

          {expandedSection === section && (
            <div className="bg-white p-4 shadow-md rounded-lg">
              {loading ? (
                <p>Loading...</p>
              ) : (
                <ResultsTable
                  headers={
                    section === "Question Answering"
                      ? [
                          "Passage",
                          "Question",
                          "User Answer",
                          "Gold Answer",
                          "Similarity",
                        ]
                      : section === "Reading Passages"
                      ? [
                          "Reference Text",
                          "Pronunciation Score",
                          "Fluency Score",
                          "Mispronounced Words",
                        ]
                      : []
                  }
                  data={
                    section === "Question Answering"
                      ? qaData.map(
                          ({
                            passage,
                            question,
                            user_answer,
                            gold_answer,
                            similarity,
                          }) => [
                            passage,
                            question,
                            user_answer,
                            gold_answer,
                            similarity,
                          ]
                        )
                      : section === "Reading Passages"
                      ? pronunciationData.map(
                          ({
                            ReferenceText,
                            PronunciationScore,
                            FinalFluencyScore,
                            MispronouncedWords,
                          }) => [
                            ReferenceText,
                            PronunciationScore,
                            FinalFluencyScore,
                            (MispronouncedWords as string[]).join(", "),
                          ]
                        )
                      : []
                  }
                />
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ResultContent;
