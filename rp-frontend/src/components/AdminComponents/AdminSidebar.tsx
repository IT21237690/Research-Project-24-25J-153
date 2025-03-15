import React, { useState } from "react";
import { FiMenu, FiX } from "react-icons/fi"; // Import icons
import { useNavigate } from "react-router-dom";

const AdminSidebar = ({ setSelectedSection }) => {
  const [isOpen, setIsOpen] = useState(true); // Sidebar open state
  const navigate = useNavigate();
  const handleLogout = () => {
    // Clear all session-related data from localStorage
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("userId");
    localStorage.removeItem("grade");
    localStorage.removeItem("role");

    console.log("User logged out, session cleared.");

    // Redirect to login page
    navigate("/login");
  };
  return (
    <div className={`relative ${isOpen ? "w-64" : "w-16"} min-h-screen bg-gray-800 text-white transition-all duration-300`}>
      
      {/* Toggle Button */}
      <button 
        className="absolute top-4 right-[-18px] bg-gray-700 p-2 rounded-full hover:bg-gray-600"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <FiX size={20} /> : <FiMenu size={20} />} {/* Show X when open, Menu when closed */}
      </button>

      <div className={`flex flex-col gap-4 p-5 ${isOpen ? "opacity-100" : "opacity-0 hidden"} transition-opacity duration-300`}>
        <h2 className="text-2xl font-bold">Admin Panel</h2>
        <button className="text-left p-2 hover:bg-gray-700 rounded" onClick={() => setSelectedSection("Teacher_Management")}>
          Teacher Management
        </button>
        <button className="text-left p-2 hover:bg-gray-700 rounded" onClick={() => setSelectedSection("Student_Management")}>
          Student Management
        </button>
        <button className="text-left p-2 hover:bg-gray-700 rounded" onClick={() => setSelectedSection("Upload_Management")}>
          Upload Management
        </button>
        <button className="text-left p-2 hover:bg-gray-700 rounded" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  );
};

export default AdminSidebar;
