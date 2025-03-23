import React from "react";
import { FaTrash } from "react-icons/fa";

interface TableProps {
  headers: string[];
  data: any[];
  onDelete?: (id: string) => void;
}

const Table = ({ headers, data, onDelete }: TableProps) => {
  // Map header names to the corresponding key names on the student object.
  const keyMapping: Record<string, string> = {
    "First Name": "firstname",
    "Last Name": "lastname",
    "User Name": "username",
    "Email": "email",
    "Grade": "grade",
    "Current Reading Difficulty": "currentDifficulty",
    "Current Fluency Difficulty": "fluencyDifficulty",
    "Interests": "interests",
    "Liked Videos": "likedVideos",
    "Watch History": "watchHistory",
    "User Created At": "createdAt",
  };

  // Delete function that calls the DELETE API endpoint.
  const handleDelete = async (id: string) => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("No token found in localStorage");
      return;
    }
    try {
      const response = await fetch(`http://localhost:8000/api/users/${id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });
      if (response.ok) {
        // Call the onDelete callback if provided.
        if (onDelete) {
          onDelete(id);
        }
      } else {
        console.error("Failed to delete user:", response.statusText);
      }
    } catch (error) {
      console.error("Error deleting user:", error);
    }
  };

  return (
    <div className="bg-white rounded-lg">
      <table className="w-full border-collapse">
        <thead className="sticky top-0 z-10">
          <tr className="bg-gray-200">
            {headers.map((header, index) => (
              <th key={index} className="px-4 py-2 border">
                {header}
              </th>
            ))}
            <th className="px-4 py-2 border">Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.length > 0 ? (
            data.map((student, rowIndex) => (
              <tr key={rowIndex} className="text-center hover:bg-gray-100">
                {headers.map((header, colIndex) => {
                  const key = keyMapping[header];
                  let value = student[key];
                  // If the value is an array, join it with commas
                  if (Array.isArray(value)) {
                    value = value.join(", ");
                  }
                  // Format createdAt as a localized date string
                  if (key === "createdAt" && value) {
                    value = new Date(value).toLocaleString();
                  }
                  return (
                    <td key={colIndex} className="px-4 py-2 border">
                      {value}
                    </td>
                  );
                })}
                <td className="px-4 py-2 border">
                  <button onClick={() => handleDelete(student.id)} title="Delete User" >
                  <FaTrash style={{ color: "red" }} />
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={headers.length + 1} className="text-center py-4 text-gray-500">
                No data available
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
