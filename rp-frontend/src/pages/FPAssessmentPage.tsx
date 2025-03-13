import React from "react";
import Header from "../components/Header.tsx";
import VoiceRecorder from "../components/StudentComponents/VoiceRecord.tsx";

const FPAssesment = () => {
  return (
    <div className="flex flex-col h-screen transparent">
    <Header/>
    <div className="flex flex-col min-h-screen bg-fp-background bg-cover bg-center justify-center items-center pt-20 pl-20 pr-20">
    <div className="flex bg-slate-300 border-4 border-dashed border-teal-500 w-full h-full max-w-[calc(100%-48px)] max-h-[calc(100%-48px)]">
    <VoiceRecorder/>
    </div>

  </div>
</div>
  );
};
export default FPAssesment;
