import React from "react";
import { Link, useNavigate } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear all session-related data from localStorage
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("userId");
    localStorage.removeItem("grade");
    localStorage.removeItem("role");
    localStorage.removeItem("passage");
    localStorage.removeItem("difficultyScore");
    localStorage.removeItem("current_difficulty");


    console.log("User logged out, session cleared.");

    // Redirect to login page
    navigate("/login");
  };
  return (
    <header className="fixed top-0 left-0 w-full bg-[#E7FBFF] text-[#1a8dc8] drop-shadow-2xl rounded-b-lg z-50 h-16 flex items-center font-header text-2xl">
      <div className="container flex justify-between items-center max-w-full px-6">
      {/*  mx-auto*/}
        {/* Logo */}
        <div className="logo">
          <Link to="/">
            <img src="/logo.png" alt="Logo" className="h-10" />
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex space-x-6 font-semibold">
          <Link to="/studentLanding" className="hover:text-blue-500">
            Home
          </Link>
          <Link onClick={handleLogout} to="/login" className="hover:text-blue-500">
            Logout
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
