import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

const Login = () => {
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent page reload

    try {
      // Call the API endpoint with the login credentials
      const response = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // Map userName to email if your API expects "email"
        body: JSON.stringify({
          username: userName,
          password: password,
        }),
      });

      if (!response.ok) {
        // Handle errors (for example, invalid credentials)
        console.error("Login failed.");
        return;
      }

      // Get the JSON response which should contain the token
      const data = await response.json();
      const token = data.token; // Adjust if your token property has a different name
      // console.log("token", token);
      // Define your custom JWT payload interface
      interface MyJwtPayload {
        username: string;
        id: string; // or number, depending on your payload
        grade: string;
        role: string;
        currentDifficulty: string;
        fluencyDifficulty: string;
        // add any other custom properties if needed
      }

      // Decode the token with the custom type
      const decoded = jwtDecode<MyJwtPayload>(token);
      const {
        username,
        id,
        grade,
        role,
        currentDifficulty,
        fluencyDifficulty,
      } = decoded;
      // console.log("payload", decoded);

      // Store the token and user details in localStorage
      localStorage.setItem("token", token);
      localStorage.setItem("username", username);
      localStorage.setItem("userId", id);
      localStorage.setItem("grade", grade);
      localStorage.setItem("role", role);
      localStorage.setItem("qnadifficultyScore", currentDifficulty);
      localStorage.setItem("fnpdifficultyScore", fluencyDifficulty);
      console.log("USER TOKEN", token);
      console.log("USER ID", id);
      // Redirect the user based on the role
      if (role === "admin") {
        navigate("/adminLanding");
      } else if (role === "teacher") {
        navigate("/teacherLanding");
      } else if (role === "student") {
        navigate("/studentLanding");
      } else {
        console.error("Unknown role:", role);
      }
    } catch (error) {
      console.error("An error occurred during login:", error);
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
            {/* Email/User Name Input */}
            <input
              type="text"
              placeholder="User Name "
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
            <button
              // type="submit"
              className="w-full bg-gray-500 text-white py-2 rounded-md hover:bg-gray-600"
              onClick={() => navigate("/")}
            >
              Back To Main
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
