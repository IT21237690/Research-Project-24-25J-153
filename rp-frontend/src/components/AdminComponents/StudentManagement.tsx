import React, { useEffect, useState } from "react";
import SearchBar from "./SearchBar.tsx";
import StudentTable from "./Tables/StudentTable.tsx";

interface Student {
  id: number;
  name: string;
  subject: string;
  email: string;
  role: string;
}

const StudentManagement = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [students, setStudents] = useState<Student[]>([]);

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
<div
  className={`p-5 shadow-lg rounded-lg h-[90vh] flex flex-col transition-all duration-300 ${
    showForm ? "bg-transparent" : "bg-pink-200"
  }`}
>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-black">
          {showForm ? "Add Student" : "Manage Student Access"}
        </h2>

        {!showForm && (
          <button
            className="bg-pink-500 text-white px-4 py-2 rounded-md hover:bg-pink-600"
            onClick={() => setShowForm(true)}
          >
            + Add Student
          </button>
        )}
      </div>

      {/* Show Form if Adding a Student */}
      {showForm ? (
        <form onSubmit={handleSubmit} className="bg-white p-5 rounded-lg shadow-lg w-full max-w-md mx-auto flex flex-col gap-4">
          <input type="text" name="firstName" placeholder="First Name" required className="border p-2 rounded-md" />
          <input type="text" name="lastName" placeholder="Last Name" required className="border p-2 rounded-md" />
          <input type="text" name="subject" placeholder="Subject" required className="border p-2 rounded-md" />
          <input type="email" name="email" placeholder="Email" required className="border p-2 rounded-md" />
          <input type="text" name="username" placeholder="Username" required className="border p-2 rounded-md" />
          <input type="password" name="password" placeholder="Password" required className="border p-2 rounded-md" />

          {/* Role (Pre-filled) */}
          <input type="text" name="role" value="Student" readOnly className="border p-2 rounded-md bg-gray-100 text-gray-500" />

          {/* Submit Button */}
          <button type="submit" className="bg-pink-500 text-white py-2 rounded-md hover:bg-pink-600">
            Add
          </button>

          {/* Cancel Button */}
          <button type="button" onClick={() => setShowForm(false)} className="bg-gray-500 text-white py-2 rounded-md hover:bg-gray-600">
            Cancel
          </button>
        </form>
      ) : (
        <>
          {/* Search Component */}
          <SearchBar onSearch={setSearchTerm} />

          {/* Scrollable Table */}
          <div className="flex-1 overflow-y-auto rounded-lg bg-white shadow-md">
            <StudentTable students={filteredStudents} />
          </div>
        </>
      )}
    </div>
  );
};

export default StudentManagement;
