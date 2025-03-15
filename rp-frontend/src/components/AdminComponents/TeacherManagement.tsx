import React, { useEffect, useState } from "react";
import SearchBar from "../AdminComponents/SearchBar.tsx";
import TeacherTable from "./Tables/TeacherTable.tsx";

interface Teacher {
  id: number;
  name: string;
  subject: string;
  email: string;
  role: string;
}

const TeacherManagement = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [teachers, setTeachers] = useState<Teacher[]>([]);

  useEffect(() => {
    setTimeout(() => {
      const fetchedTeachers: Teacher[] = [
        { id: 1, name: "John Doe", subject: "Mathematics", email: "john@example.com", role: "Teacher" },
        { id: 2, name: "Jane Smith", subject: "English", email: "jane@example.com", role: "Teacher" },
        { id: 3, name: "Alice Johnson", subject: "Science", email: "alice@example.com", role: "Teacher" },
      ];
      setTeachers(fetchedTeachers);
    }, 1000);
  }, []);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    // Ensure values are always strings
    const newTeacher: Teacher = {
      id: teachers.length + 1,
      name: `${formData.get("firstName") as string} ${formData.get("lastName") as string}`,
      subject: formData.get("subject") as string,
      email: formData.get("email") as string,
      role: "Teacher", // Fixed role
    };

    setTeachers([...teachers, newTeacher]);
    setShowForm(false); // Switch back to table view
  };

  // Filter teachers based on search term
  const filteredTeachers = teachers.filter((teacher) =>
    teacher.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
<div
  className={`p-5 shadow-lg rounded-lg h-[90vh] flex flex-col transition-all duration-300 ${
    showForm ? "bg-transparent" : "bg-teal-200"
  }`}
>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-black">
          {showForm ? "Add Teacher" : "Manage Teacher Access"}
        </h2>

        {!showForm && (
          <button
            className="bg-teal-500 text-white px-4 py-2 rounded-md hover:bg-teal-600"
            onClick={() => setShowForm(true)}
          >
            + Add Teacher
          </button>
        )}
      </div>

      {/* Show Form if Adding a Teacher */}
      {showForm ? (
        <form onSubmit={handleSubmit} className="bg-white p-5 rounded-lg shadow-lg w-full max-w-md mx-auto flex flex-col gap-4">
          <input type="text" name="firstName" placeholder="First Name" required className="border p-2 rounded-md" />
          <input type="text" name="lastName" placeholder="Last Name" required className="border p-2 rounded-md" />
          <input type="text" name="subject" placeholder="Subject" required className="border p-2 rounded-md" />
          <input type="email" name="email" placeholder="Email" required className="border p-2 rounded-md" />
          <input type="text" name="username" placeholder="Username" required className="border p-2 rounded-md" />
          <input type="password" name="password" placeholder="Password" required className="border p-2 rounded-md" />

          {/* Role (Pre-filled) */}
          <input type="text" name="role" value="Teacher" readOnly className="border p-2 rounded-md bg-gray-100 text-gray-500" />

          {/* Submit Button */}
          <button type="submit" className="bg-teal-500 text-white py-2 rounded-md hover:bg-green-600">
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
            <TeacherTable teachers={filteredTeachers} />
          </div>
        </>
      )}
    </div>
  );
};

export default TeacherManagement;
