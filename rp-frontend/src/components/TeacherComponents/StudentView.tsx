import React, { useContext, useEffect, useState } from "react";
import StudentTable from "../AdminComponents/Tables/StudentTable.tsx";
import SearchBar from "../AdminComponents/SearchBar.tsx";
// import { WebSocketContext } from "../../context/webSocketProvider.tsx";

interface Student {
  id: number;
  name: string;
  subject: string;
  email: string;
  role: string;
}

const StudentView = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [students, setStudents] = useState<Student[]>([]);
  // const ws = useContext(WebSocketContext); // Access WebSocket

  useEffect(() => {
    setTimeout(() => {
      const fetchedStudents: Student[] = [
        { id: 1, name: "student John Doe", subject: "Mathematics", email: "john@example.com", role: "Student" },
        { id: 2, name: "student Jane Smith", subject: "English", email: "jane@example.com", role: "Student" },
        { id: 3, name: "student Alice Johnson", subject: "Science", email: "alice@example.com", role: "Student" },
      ];
      setStudents(fetchedStudents);
    }, 1000);
  }, []);


  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    // Ensure values are always strings
    const newStudent: Student = {
      id: students.length + 1,
      name: `${formData.get("firstName") as string} ${formData.get("lastName") as string}`,
      subject: formData.get("subject") as string,
      email: formData.get("email") as string,
      role: "Student", // Fixed role
    };

    setStudents([...students, newStudent]);
    setShowForm(false); // Switch back to table view
  };

  // Filter students based on search term
  const filteredStudents = students.filter((student) =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
        <StudentTable students={filteredStudents} />
      </div>
    </div>
  );
}

export default StudentView;