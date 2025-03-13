import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login.tsx";
import React from "react";
import FPAssesment from "./pages/FPAssessmentPage.tsx";
import QnAAssessment from "./pages/QnAAssessmentPage.tsx";
import StudentLandingPage from "./pages/StudentLandingPage.tsx";
import AdminLandingPage from "./pages/AdminLandingPage.tsx";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/adminLanding" element={<AdminLandingPage />} />
        <Route path="/studentLanding" element={<StudentLandingPage/>} />
        <Route path="/fluencyAssessment" element={<FPAssesment />} />
        <Route path="/answerAssessment" element={<QnAAssessment />} />
      </Routes>
    </Router>
  );
}

export default App;
