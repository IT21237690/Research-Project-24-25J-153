import React, { useEffect, useState } from "react";
import Sidebar from "../components/AdminComponents/AdminSidebar.tsx";
import AdminContent from "../components/AdminComponents/AdminContent.tsx";

const AdminLandingPage = () => {
    // Load selected section from localStorage or default to "Teacher_Management"
    const [selectedSection, setSelectedSection] = useState(
      localStorage.getItem("selectedSection") || "Teacher_Management"
    );
  
    // Save to localStorage whenever selectedSection changes
    useEffect(() => {
      localStorage.setItem("selectedSection", selectedSection);
    }, [selectedSection]);
  return (
    <div className="flex flex-col h-screen">
      {/* <Header /> */}
      <div className="flex min-h-screen bg-admin-landing-background bg-cover bg-center">
        {/* Sidebar */}
        <Sidebar setSelectedSection={setSelectedSection} />

        {/* Content */}
        <AdminContent selectedSection={selectedSection}  />
      </div>
    </div>
  );

};
export default AdminLandingPage;
