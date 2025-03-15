import React from "react";
import Header from "../components/Header.tsx";
import { useNavigate } from "react-router-dom";

const StudentLandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-screen transparent">
      {/* Fixed Header */}
      <Header />

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto mt-16 min-h-screen bg-student-landing-background bg-cover bg-center">
        {/* Card Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-10 bg-transparent">
          <button onClick={() => navigate("/fluencyAssessment")}>
            <Card
              // className="text-white bg-green-600 font-button font-semibold"
              className="text-white bg-gradient-to-br from-pink-500 to-orange-400 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2"
              title="Talk Like a Star!"
              description="Description of feature 1"
            />
          </button>
          <button onClick={() => navigate("/answerAssessment")}>
            <Card
              title="Start Answering!"
              description="Enhance reading comprehension."
              className="text-white bg-gradient-to-r from-cyan-500 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-cyan-300 dark:focus:ring-cyan-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2"
            />
          </button>
          <Card
            className="text-white bg-gradient-to-br from-green-400 to-blue-600 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-green-200 dark:focus:ring-green-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2"
            title="Play & Level Up!"
            description="Description of feature 3"
          />
          <Card
            className="text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:bg-gradient-to-l focus:ring-4 focus:outline-none focus:ring-purple-200 dark:focus:ring-purple-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2"
            title="See & Describe!"
            description="Description of feature 4"
          />
        </div>
      </div>
    </div>
  );
};

const Card = ({ title, description, className }) => {
  return (
    <div className={`p-6 text-center rounded-xl shadow-lg ${className}`}>
      <h2 className="text-xl font-bold">{title}</h2>
      <p className="mt-2">{description}</p>
    </div>
  );
};

export default StudentLandingPage;

// "text-white bg-gradient-to-br from-purple-600 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Purple to Blue</button>
// "text-white bg-gradient-to-r from-cyan-500 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-cyan-300 dark:focus:ring-cyan-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Cyan to Blue</button>
// "text-white bg-gradient-to-br from-4 to-blue-600 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-green-200 dark:focus:ring-green-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Green to Blue</button>
// "text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:bg-gradient-to-l focus:ring-4 focus:outline-none focus:ring-purple-200 dark:focus:ring-purple-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Purple to Pink</button>
// "text-white bg-gradient-to-br from-pink-500 to-orange-400 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Pink to Orange</button>
