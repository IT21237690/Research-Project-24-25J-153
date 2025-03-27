import React from "react";
import Header from "../components/Header.tsx";
import ResultContent from "../components/StudentComponents/ResultsConent.tsx";

const StudentProfile = () => {
  const storedUsername = localStorage.getItem("username") || "Student";

  return (
    <div className="flex flex-col h-screen transparent">
      <Header />
      <div className="flex flex-col min-h-screen bg-student-profile-background bg-cover bg-center justify-start items-center pt-10 px-10 w-full">
        <div className="text-8xl font-bold mb-6 mt-12 bg-gradient-to-r from-blue-700 to-pink-700 text-transparent bg-clip-text">
          Hi {storedUsername} 
        </div>

        <ResultContent />
      </div>
    </div>
  );
};
export default StudentProfile;
