import React from "react";
import Header from "../components/Header.tsx";
import DisplayQuestion from "../components/StudentComponents/DisplayQuestion.tsx";
import AnswerContent from "../components/StudentComponents/AnswerContent.tsx";

const QnAAssessment = () => {
  return (
    <div className="flex flex-col h-screen transparent">
      <Header />
      <div className="flex flex-col min-h-screen bg-qa-background bg-cover bg-center justify-start items-center pt-10 px-10 w-full">
        {/* <div className="flex bg-slate-300 border-4 border-dashed border-teal-500 w-full h-full max-w-[calc(100%-48px)] max-h-[calc(100%-48px)]"> */}
        <DisplayQuestion />

        <AnswerContent />
        
        
        
        </div>
        
      {/* </div> */}
    </div>
  );
};
export default QnAAssessment;
