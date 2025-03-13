import React from "react";
import TeacherManagement from "./TeacherManagement.tsx";
import StudentManagement from "./StudentManagement.tsx";
import UploadManagement from "./UploadManagement.tsx";

const AdminContent = ({ selectedSection}) => {
  
  return (
    <div className="flex-1 min-h-screen p-10 shadow-lg overflow-hidden">
      {selectedSection === "Teacher_Management" && <TeacherManagement />}
      {selectedSection === "Student_Management" && <StudentManagement/>}
      {selectedSection === "Upload_Management" && <UploadManagement/>}
    </div>
  );
};

export default AdminContent;
