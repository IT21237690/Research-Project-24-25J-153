import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login.tsx";
import React from "react";
import FPAssesment from "./pages/FPAssessmentPage.tsx";
import QnAAssessment from "./pages/QnAAssessmentPage.tsx";
import StudentLandingPage from "./pages/StudentLandingPage.tsx";
import AdminLandingPage from "./pages/AdminLandingPage.tsx";
import TeacherLandingPage from "./pages/TeacherLandingPage.tsx";
import MainLanding from "./pages/MainLanding.tsx";
import { SoundProvider } from "./context/Sound.context.tsx";

function App() {
  return (
    <SoundProvider>
    <Router>
      <Routes>
      <Route path="/" element={<MainLanding />} />
        <Route path="/login" element={<Login />} />
        <Route path="/adminLanding" element={<AdminLandingPage />} />
        <Route path="/teacherLanding" element={<TeacherLandingPage />} />
        <Route path="/studentLanding" element={<StudentLandingPage/>} />
        <Route path="/fluencyAssessment" element={<FPAssesment />} />
        <Route path="/answerAssessment" element={<QnAAssessment />} />
      </Routes>
    </Router>
    </SoundProvider>
  );
}

export default App;
