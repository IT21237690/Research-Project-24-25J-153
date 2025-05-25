import React, { useRef } from "react";
import Header from "../components/Header.tsx";
import { useNavigate } from "react-router-dom";
import { useSound } from "../context/Sound.context.tsx";

const StudentLandingPage = () => {
  const navigate = useNavigate();
  const mainClickRef = useRef<HTMLAudioElement>(null);
  const { soundEnabled } = useSound();

  const handleMainClick = (path: string) => {
    if (soundEnabled && mainClickRef.current) {
      mainClickRef.current.play().catch((err) => {
        console.warn("Audio playback failed:", err);
      });
    }
  
    // Optional delay
    setTimeout(() => navigate(path), 350);
  };
  return (
    <div className="flex flex-col h-screen transparent">
      {/* Fixed Header */}
      <Header />

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto mt-16 min-h-screen bg-student-landing-background bg-cover bg-center">
        

        <div className="bg-transparent text-center text-4xl p-4 md:text-5xl font-extrabold w-full min-h-content mt-24">
          <h1 className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-pink-500 to-purple-500 animate-pulse">
            Hey there, little explorer!
          </h1>
          <h2 className="text-transparent bg-clip-text bg-gradient-to-r from-green-500 via-yellow-500 to-orange-500 mt-2 animate-bounce">
            Welcome to Little Geek English
          </h2>
          <p className="text-lg text-gray-200 mt-4  text-green-900">
            Let's start your learning adventure!
          </p>
        </div>

        {/* Card Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-10 bg-transparent ">
        <audio
          ref={mainClickRef}
          src="/sounds/mainButtonClick.mp3"
          preload="auto"
        />
          <div className="w-full flex items-center justify-center bg-white/30 backdrop-blur-lg border border-white/40 p-2 pt-8 pb-4 rounded-lg shadow-lg">
            <button onClick={() => handleMainClick("/fluencyAssessment")}>
              <Card
                className="max-w-xs text-white bg-gradient-to-br from-pink-500 to-orange-400 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 font-extrabold rounded-full text-4xl tracking-wide px-8 py-4 text-center me-2 mb-2 transform transition-transform hover:scale-105 active:scale-95"
                title="⭐ Talk Like a Star!"
              />
            </button>
          </div>

          <div className="w-full flex items-center justify-center bg-white/30 backdrop-blur-lg border border-white/40 p-2 pt-8 pb-4 rounded-lg shadow-lg">
            <button onClick={() => handleMainClick("/answerAssessment")}>
              <Card
                title="✏️ Start Answering!"
                className="max-w-xs text-white bg-gradient-to-r from-cyan-500 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-cyan-300 dark:focus:ring-cyan-800 font-extrabold rounded-full text-4xl tracking-wide px-8 py-4 text-center me-2 mb-2 transform transition-transform hover:scale-105 active:scale-95"
              />
            </button>
          </div>
          <div className="w-full flex items-center justify-center bg-white/30 backdrop-blur-lg border border-white/40 p-2 pt-8 pb-4 rounded-lg shadow-lg">
            <Card
              className="max-w-xs text-white bg-gradient-to-br from-green-400 to-blue-600 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-green-200 dark:focus:ring-green-800 font-extrabold rounded-lg text-2xl tracking-wide px-5 py-2.5 text-center me-2 mb-2 transform transition-transform hover:scale-105 active:scale-95"
              title="Play & Level Up!"
            />
          </div>
          <div className="w-full flex items-center justify-center bg-white/30 backdrop-blur-lg border border-white/40 p-2 pt-8 pb-4 rounded-lg shadow-lg">
            <button onClick={() => handleMainClick("/imageDesc")}>
            <Card
              className="max-w-xs text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:bg-gradient-to-l focus:ring-4 focus:outline-none focus:ring-purple-200 dark:focus:ring-purple-800 font-extrabold rounded-lg text-2xl tracking-wide px-5 py-2.5 text-center me-2 mb-2 transform transition-transform hover:scale-105 active:scale-95"
              title="See & Describe!"
            />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const Card = ({ title, className }) => {
  return (
    <div className={`p-6 text-center rounded-xl shadow-lg ${className}`}>
      <h2 className="text-xl font-bold">{title}</h2>
      {/* <p className="mt-2">{description}</p> */}
    </div>
  );
};

export default StudentLandingPage;

// "text-white bg-gradient-to-br from-purple-600 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Purple to Blue</button>
// "text-white bg-gradient-to-r from-cyan-500 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-cyan-300 dark:focus:ring-cyan-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Cyan to Blue</button>
// "text-white bg-gradient-to-br from-4 to-blue-600 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-green-200 dark:focus:ring-green-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Green to Blue</button>
// "text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:bg-gradient-to-l focus:ring-4 focus:outline-none focus:ring-purple-200 dark:focus:ring-purple-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Purple to Pink</button>
// "text-white bg-gradient-to-br from-pink-500 to-orange-400 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">Pink to Orange</button>
