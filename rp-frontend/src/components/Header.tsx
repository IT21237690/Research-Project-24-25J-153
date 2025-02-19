// import React from "react";
// import { Link } from "react-router-dom";
// import "../styles/theme.css"; // Import the theme.css file

// const Header = () => {
//   return (
//     <header className="header ">
//       <div className="header-container">
//         {/* Logo on the Left */}
//         <div className="logo">
//           <Link to="/">
//             <img src="/logo.png" alt="Logo" />
//           </Link>
//         </div>

//         {/* Navigation Links on the Right */}
//         <div>
//           <div className="nav-links">
//             <div>
//               <Link to="/">Home</Link>
//             </div>
//             <div>
//               <Link to="/login">Login</Link>
//             </div>
//           </div>
//         </div>
//       </div>
//     </header>
//   );
// };

// export default Header;



import React from "react";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="fixed top-0 left-0 w-full bg-[#E7FBFF] text-[#1a8dc8] shadow-md z-50 h-16 flex items-center">
      <div className="container mx-auto flex justify-between items-center px-6">
        {/* Logo */}
        <div className="logo">
          <Link to="/">
            <img src="/logo.png" alt="Logo" className="h-10" />
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex space-x-6 font-semibold">
          <Link to="/" className="hover:text-blue-500">Home</Link>
          <Link to="/login" className="hover:text-blue-500">Login</Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
