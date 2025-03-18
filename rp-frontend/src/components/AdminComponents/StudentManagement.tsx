import React, { useEffect, useState } from "react";
import SearchBar from "./SearchBar.tsx";
import Table from "./Tables/Table.tsx";

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

const StudentManagement = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [students, setStudents] = useState<Student[]>([]);
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
        const studentData = data.filter((user: any) => user.role === "student");
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
  useEffect(() => {
    fetchStudents();
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    // Build the payload as expected by your API
    const newStudentPayload = {
      firstname: formData.get("firstName") as string,
      lastname: formData.get("lastName") as string,
      username: formData.get("username") as string,
      email: formData.get("email") as string,
      password: formData.get("password") as string, // make sure your form includes a password input
      role: "student",
      grade: formData.get("grade") as string,
    };

    try {
      const response = await fetch("http://localhost:8000/api/auth/add/user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newStudentPayload),
      });
      if (response.ok) {
        // Parse the returned student data
        const studentData = await response.json();
        // Update the local state with the new student (mapping API fields to your Student interface)
        setStudents([
          ...students,
          {
            id: studentData._id, // using _id from the response
            firstname: studentData.firstname,
            lastname: studentData.lastname,
            username: studentData.username,
            email: studentData.email,
            grade: studentData.grade,
            currentDifficulty: studentData.currentDifficulty, // default provided by API
            fluencyDifficulty: studentData.fluencyDifficulty, // default provided by API
            interests: studentData.interests, // default provided by API
            likedVideos: studentData.likedVideos, // default provided by API
            watchHistory: studentData.watchHistory, // default provided by API
            createdAt: studentData.createdAt,
          },
        ]);
        setShowForm(false);
        fetchStudents();
      } else {
        console.error("Error adding student:", response.statusText);
      }
    } catch (error) {
      console.error("Error adding student:", error);
    }
  };

  // Filter students by matching the search term in first name and last name
  const filteredStudents = students.filter((student) =>
    `${student.firstname} ${student.lastname}`
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  // Define headers for the table.
  const headers = [
    "First Name",
    "Last Name",
    "User Name",
    "Email",
    "Grade",
    "Current Reading Difficulty",
    "Current Fluency Difficulty",
    "Interests",
    "Liked Videos",
    "Watch History",
    "User Created At",
  ];

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

      {showForm ? (
        <form
          onSubmit={handleSubmit}
          className="bg-white p-5 rounded-lg shadow-lg w-full max-w-md mx-auto flex flex-col gap-4"
        >
          <input
            type="text"
            name="firstName"
            placeholder="First Name"
            required
            className="border p-2 rounded-md"
          />
          <input
            type="text"
            name="lastName"
            placeholder="Last Name"
            required
            className="border p-2 rounded-md"
          />
          <input
            type="text"
            name="username"
            placeholder="User Name"
            required
            className="border p-2 rounded-md"
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            required
            className="border p-2 rounded-md"
          />
          <input
            type="text"
            name="grade"
            placeholder="Grade"
            required
            className="border p-2 rounded-md"
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            required
            className="border p-2 rounded-md"
          />

          {/* You can add additional inputs for interests, likedVideos, and watchHistory if needed */}
          <button
            type="submit"
            className="bg-pink-500 text-white py-2 rounded-md hover:bg-pink-600"
          >
            Add
          </button>
          <button
            type="button"
            onClick={() => setShowForm(false)}
            className="bg-gray-500 text-white py-2 rounded-md hover:bg-gray-600"
          >
            Cancel
          </button>
        </form>
      ) : (
        <>
          <SearchBar onSearch={setSearchTerm} />
          <div className="flex-1 overflow-y-auto rounded-lg bg-white shadow-md">
            <Table
              headers={headers}
              data={filteredStudents}
              onDelete={(id: string) =>
                setStudents((prev) =>
                  prev.filter((student) => student.id !== id)
                )
              }
            />
          </div>
        </>
      )}
    </div>
  );
};

export default StudentManagement;
