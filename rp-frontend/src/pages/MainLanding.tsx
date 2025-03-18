import React from "react";
import { useNavigate } from "react-router-dom";
import { FaGamepad, FaBookOpen, FaImage, FaPenFancy } from "react-icons/fa"; // Importing React Icons
import MainHeader from "../components/MainHeader.tsx";

const MainLanding = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-screen bg-main-landing-background bg-cover bg-center bg-no-repeat">
  <MainHeader />

  {/* Main Content with Glass Effect */}
  <div className="flex-1 flex flex-col justify-center items-center text-center px-6 bg-white/40 rounded-lg">
    {/* Animated Heading */}
    <h1 className="text-6xl md:text-7xl font-extrabold bg-gradient-to-r from-gray-900 to-red-500 text-transparent bg-clip-text animate-bounce">
      Welcome to LITTLE GEEEK ENGLISH!
    </h1>

    <p className="mt-4 text-2xl font-extrabold text-transparent bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text max-w-2xl">
      A fun and exciting way for young learners to improve English!  
      Engage in interactive activities like:
    </p>

    {/* Features Section */}
    <div className="mt-6 flex flex-wrap justify-center gap-8">
      <div className="flex flex-col items-center group">
        <FaBookOpen className="text-yellow-400 text-6xl mb-2 group-hover:scale-110 transition-transform" />
        <p className="text-white text-lg font-bold">Read Aloud</p>
      </div>
      <div className="flex flex-col items-center group">
        <FaGamepad className="text-green-400 text-6xl mb-2 group-hover:scale-110 transition-transform" />
        <p className="text-white text-lg font-bold">Fun Games</p>
      </div>
      <div className="flex flex-col items-center group">
        <FaImage className="text-red-400 text-6xl mb-2 group-hover:scale-110 transition-transform" />
        <p className="text-white text-lg font-bold">Image Description</p>
      </div>
      <div className="flex flex-col items-center group">
        <FaPenFancy className="text-blue-400 text-6xl mb-2 group-hover:scale-110 transition-transform" />
        <p className="text-white text-lg font-bold">Read & Answer</p>
      </div>
    </div>

    {/* Login Button */}
    <button
      onClick={() => navigate("/login")}
      className="mt-6 px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold text-xl rounded-lg shadow-lg hover:scale-110 transition-transform flex items-center gap-2"
    >
      🚀 Start Learning  
    </button>
  </div>
</div>

  );
};

export default MainLanding;
