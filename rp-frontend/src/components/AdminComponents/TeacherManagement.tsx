import React, { useEffect, useState } from "react";
import SearchBar from "../AdminComponents/SearchBar.tsx";
import Table from "./Tables/Table.tsx";

interface Teacher {
  id: string;
  firstname: string;
  lastname: string;
  username: string;
  email: string;
  grade: string;
}

const TeacherManagement = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const fetchTeachers = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("No token found in localStorage");
      return;
    }
    try {
      const response = await fetch("http://20.193.146.113:5000/api/users", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        const data = await response.json();
        // Filter only users with role "student"
        const teacherData = data.filter(
          (user: any) => user.role === "teacher"
        );
        // Map API response fields to our Student interface
        const mappedTeachers: Teacher[] = teacherData.map((user: any) => ({
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
        setTeachers(mappedTeachers);
      } else {
        console.error("Error fetching users: ", response.statusText);
      }
    } catch (error) {
      console.error("Error fetching users: ", error);
    }
  };
  useEffect(() => {
  

    fetchTeachers();
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
      role: "teacher",
      grade: "0",
    };

    try {
      const response = await fetch("http://20.193.146.113:5000/api/auth/add/user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newStudentPayload),
      });
      if (response.ok) {
        // Parse the returned student data
        const teacherData = await response.json();
        // Update the local state with the new student (mapping API fields to your Student interface)
        setTeachers([
          ...teachers,
          {
            id: teacherData._id, // using _id from the response
            firstname: teacherData.firstname,
            lastname: teacherData.lastname,
            username: teacherData.username,
            email: teacherData.email,
            grade: "0"
          },
        ]);
        setShowForm(false);
        fetchTeachers();
      } else {
        console.error("Error adding teacher:", response.statusText);
      }
    } catch (error) {
      console.error("Error adding teacher:", error);
    }
  };
  const filteredTeachers = teachers.filter((teacher) =>
    `${teacher.firstname} ${teacher.lastname}`
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

   // Define headers for the table.
   const headers = [
    "First Name",
    "Last Name",
    "User Name",
    "Email",
  ];

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
            type="email"
            name="email"
            placeholder="Email"
            required
            className="border p-2 rounded-md"
          />
          <input
            type="text"
            name="username"
            placeholder="Username"
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

          {/* Role (Pre-filled) */}
          <input
            type="text"
            name="role"
            value="Teacher"
            readOnly
            className="border p-2 rounded-md bg-gray-100 text-gray-500"
          />

          {/* Submit Button */}
          <button
            type="submit"
            className="bg-teal-500 text-white py-2 rounded-md hover:bg-teal-600"
          >
            Add
          </button>

          {/* Cancel Button */}
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
          {/* Search Component */}
          <SearchBar onSearch={setSearchTerm} />

          {/* Scrollable Table */}
          <div className="flex-1 overflow-y-auto rounded-lg bg-white shadow-md">
            {/* Pass dynamic headers and filtered data to TeacherTable */}
            <Table
              headers={headers}
              data={filteredTeachers}
              onDelete={(id: string) =>
                setTeachers((prev) =>
                  prev.filter((teacher) => teacher.id !== id)
                )
              }
            />          </div>
        </>
      )}
    </div>
  );
};

export default TeacherManagement;
