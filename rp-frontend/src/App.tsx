import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage.tsx";
import Login from "./pages/Login.tsx";
import Register from "./pages/Register.tsx";
import React from "react";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register onRegister={undefined} />} />
      </Routes>
    </Router>
  );
}

export default App;
