import { useState } from "react";
import { useNavigate } from "react-router-dom";
import React from "react";

const Login = () => {
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent page reload

    // Check credentials
    if (userName === "admin" && password === "admin") {
      navigate("/adminLanding"); // Redirect to /a for admin
    } else {
      navigate("/studentLanding"); // Redirect to /b for normal users
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Main Content */}
      <div className="relative flex-1 flex justify-center items-center bg-login-background bg-cover bg-center">
        {/* Blur Overlay */}
        <div className="absolute inset-0 bg-black/30 backdrop-blur-sm"></div>

        {/* Login Box - Kept Clear */}
        <div
          className="relative z-10 bg-slate-300 border-4 border-dashed border-teal-500 
                px-8 py-10 w-full max-w-md rounded-lg shadow-lg flex flex-col items-center"
        >
          {/* Login Title */}
          <h2 className="text-2xl font-bold mb-4">Login</h2>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
            {/* Email Input */}
            <input
              type="text"
              placeholder="User Name"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-400 rounded-md"
              required
            />

            {/* Password Input */}
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-400 rounded-md"
              required
            />

            {/* Login Button */}
            <button
              type="submit"
              className="w-full bg-teal-500 text-white py-2 rounded-md hover:bg-teal-600"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
