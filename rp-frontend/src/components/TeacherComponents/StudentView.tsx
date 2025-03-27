import React, { useContext, useEffect, useState } from "react";
import Table from "../AdminComponents/Tables/Table.tsx";
import SearchBar from "../AdminComponents/SearchBar.tsx";

interface Student {
  id: string;
  firstname: string;
  lastname: string;
  username: string;
  email: string;
  grade: string;
  currentDifficulty: number;
  fluencyDifficulty: number;
  interests: string[];
  likedVideos: string[];
  watchHistory: string[];
  createdAt: string;
}
const StudentView = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [students, setStudents] = useState<Student[]>([]);

  useEffect(() => {
     const fetchStudents = async () => {
       const token = localStorage.getItem("token");
       if (!token) {
         console.error("No token found in localStorage");
         return;
       }
       try {
         const response = await fetch("http://localhost:8000/api/users", {
           method: "GET",
           headers: {
             Authorization: `Bearer ${token}`,
             "Content-Type": "application/json",
           },
         });
         if (response.ok) {
           const data = await response.json();
           // Filter only users with role "student"
           const studentData = data.filter(
             (user: any) => user.role === "student"
           );
           // Map API response fields to our Student interface
           const mappedStudents: Student[] = studentData.map((user: any) => ({
             id: user._id,
             firstname: user.firstname,
             lastname: user.lastname,
             username: user.username,
             email: user.email,
             grade: user.grade,
             currentDifficulty: user.currentDifficulty,
             fluencyDifficulty: user.fluencyDifficulty,
             interests: user.interests,
             likedVideos: user.likedVideos,
             watchHistory: user.watchHistory,
             createdAt: user.createdAt,
           }));
           setStudents(mappedStudents);
         } else {
           console.error("Error fetching users: ", response.statusText);
         }
       } catch (error) {
         console.error("Error fetching users: ", error);
       }
     };
 
     fetchStudents();
   }, []);

  // Filter students based on search term
  const filteredStudents = students.filter((student) =>
    `${student.firstname} ${student.lastname}`
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  // Get dynamic headers (keys from the first student object)
 // Define headers for the table.
 const headers = [
  "First Name",
  "Last Name",
  "User Name",
  "Grade",
  "Current Reading Difficulty",
  "Current Fluency Difficulty",
  "Interests",
  "Liked Videos",
  "Watch History",
];

  return (
    <div className="p-5 shadow-lg rounded-lg h-[90vh] flex flex-col transition-all duration-300 bg-pink-200">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-black">Student Detail View</h2>
      </div>

      {/* Search Component */}
      <SearchBar onSearch={setSearchTerm} />

      {/* Scrollable Table */}
      <div className="flex-1 overflow-y-auto rounded-lg bg-white shadow-md">
        {/* Pass headers and filtered data */}
        <Table headers={headers} data={filteredStudents} />
      </div>
    </div>
  );
};

export default StudentView;
