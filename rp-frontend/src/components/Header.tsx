import React from "react";
import { Link } from "react-router-dom";
import "../styles/theme.css"; // Import the theme.css file

const Header = () => {
  return (
    <header className="header ">
      <div className="header-container">
        {/* Logo on the Left */}
        <div className="logo">
          <Link to="/">
            <img src="/logo.png" alt="Logo" />
          </Link>
        </div>

        {/* Navigation Links on the Right */}
        <div>
          <div className="nav-links">
            <div>
              <Link to="/">Home</Link>
            </div>
            <div>
              <Link to="/login">Login</Link>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
