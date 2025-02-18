import React from "react";
import "../styles/theme.css"; // Import styles
import Header from "../components/Header.tsx";

const LandingPage = () => {
  return (
    <>
      <Header />
      <div className="page-container">
        <div className="body-container ">
          <div style={{   }}>
            <img
              src="/assets/green_tree.svg"
              alt="Green Tree"
              className="leftImage"
            />
            <div>hi</div>
          </div>
        {/* <div className=" div-container bg-slate-600 flex"><div className="bg-pink-400 100vw">hi</div><div className="bg-blue-400">hi</div></div> */}

        </div>
      </div>
    </>
  );
};

export default LandingPage;
