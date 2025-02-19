// import React from "react";
// import "../styles/theme.css"; // Import styles
// import Header from "../components/Header.tsx";

// const LandingPage = () => {
//   return (
//     <>
//       <Header />
//       <div className="page-container">
//         <div className="body-container ">

//           {/* <div style={{   }}> */}
//             <img
//               src="/assets/Desktop.svg"
//               alt="Green Tree"
//               className="leftImage"
//             />
//             <div>hi</div>
//           {/* </div> */}
//         {/* <div className=" div-container bg-slate-600 flex"><div className="bg-pink-400 100vw">hi</div><div className="bg-blue-400">hi</div></div> */}

//         </div>
//       </div>
//     </>
//   );
// };

// export default LandingPage;

import React from "react";
import Header from "../components/Header.tsx";

const LandingPage = () => {
  return (
    <div className="flex flex-col h-screen bg-black">
      {/* Fixed Header */}
      <Header />

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto mt-16 h-screen bg-slate-200">
  {/* Full-Screen Responsive Image */}
  <div className="relative w-full h-screen flex items-center justify-center">
    <img
      src="/assets/LandingPageBlob.svg"
      alt="Landing Background"
      className="w-full h-full max-w-full max-h-full object-contain"
    />
  </div>

        {/* Card Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-10 bg-slate-200">
          <Card title="Talk Like a Star!" description="Description of feature 1" />
          <Card title="Read & Conquer!" description="Description of feature 2" />
          <Card title="Play & Level Up!" description="Description of feature 3" />
          <Card title="See & Describe!" description="Description of feature 4" />
        </div>
      </div>
    </div>
  );
};

const Card = ({ title, description }) => {
  return (
    <div className="bg-white shadow-lg rounded-xl p-6 text-center">
      <h2 className="text-xl font-bold">{title}</h2>
      <p className="text-gray-600 mt-2">{description}</p>
    </div>
  );
};

export default LandingPage;
