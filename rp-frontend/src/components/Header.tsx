import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useSound } from "../context/Sound.context.tsx";
import { HiSpeakerWave, HiSpeakerXMark } from "react-icons/hi2";
import { IoPersonCircle } from "react-icons/io5";

const Header = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear all session-related data from localStorage
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("userId");
    localStorage.removeItem("grade");
    localStorage.removeItem("role");
    localStorage.removeItem("fnppassage");
    localStorage.removeItem("difficultyScore");
    localStorage.removeItem("current_difficulty");
    localStorage.removeItem("qnapassage");

    // console.log("User logged out, session cleared.");

    // Redirect to login page
    navigate("/login");
  };
  const { soundEnabled, toggleSound } = useSound();

  return (
    <header className="fixed top-0 left-0 w-full bg-[#E7FBFF] text-[#1a8dc8] drop-shadow-2xl rounded-b-lg z-50 h-16 flex items-center font-header text-2xl">
      <div className="flex justify-between items-center w-full px-6">
        {/* Left: Logo */}
        <div className="logo">
          <img src="/assets/Logo.png" alt="Logo" className="h-48 w-48 mt-20" />
        </div>

        {/* Right: Navigation + Sound Toggle */}
        <div className="flex items-center  justify-center space-x-6 font-semibold">
          <nav className="flex space-x-6">
            <Link to="/studentLanding" className="hover:text-blue-500">
              Home
            </Link>
            <button
            onClick={toggleSound}
            className="text-5xl hover:text-blue-500 transition-colors"
            title={soundEnabled ? "Sound On" : "Sound Off"}
          >
            {soundEnabled ? <HiSpeakerWave /> : <HiSpeakerXMark />}
          </button>
          <button
            onClick={() => navigate("/studentprofile")}
            className="text-5xl hover:text-blue-500 transition-colors"
          >
            <IoPersonCircle />
          </button>
            <Link
              onClick={handleLogout}
              to="/login"
              className="hover:text-blue-500"
            >
              Logout
            </Link>
          </nav>
          
        </div>
      </div>
    </header>
  );
};

export default Header;
