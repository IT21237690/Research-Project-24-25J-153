import React from "react";
import { Link, useNavigate } from "react-router-dom";

const MainHeader = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/login");
  };
  return (
    <header className="fixed top-0 left-0 w-full bg-[#E7FBFF] text-[#1a8dc8] drop-shadow-2xl rounded-b-lg z-50 h-16 flex items-center font-header text-2xl">
      <div className="container flex justify-between items-center max-w-full px-6">
      {/*  mx-auto*/}
        {/* Logo */}
        <div className="logo">
          {/* <Link to="/"> */}
          <img src="/assets/Logo.png" alt="Logo" className="h-48 w-48 mt-20" />
          {/* </Link> */}
        </div>

        {/* Navigation */}
        <nav className="flex space-x-6 font-semibold">
          <Link onClick={handleLogin} to="/login" className="hover:text-blue-500">
            LOGIN 
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default MainHeader;
