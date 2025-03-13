import React, { useEffect, useState } from "react";
import SearchBar from "./SearchBar.tsx";
import UploadTable from "./Tables/UploadTable.tsx";

interface File {
  id: number;
  filename: string;
  username: string;
  grade: string;
  file: string;
}

const UploadManagement = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [files, setFiles] = useState<File[]>([]);

  useEffect(() => {
    setTimeout(() => {
      const fetchedFiles: File[] = [
        { id: 1, filename: "John Doe", username: "JD", grade: "3", file:"hi"}
      ];
      setFiles(fetchedFiles);
    }, 1000);
  }, []);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    // Ensure values are always strings
    const newFile: File = {
      id: files.length + 1,
      filename: `${formData.get("firstName") as string} ${formData.get("firstName") as string}`,
      username: `${formData.get("userName") as string} ${formData.get("firstName") as string}`,
      grade: `${formData.get("grade") as string} ${formData.get("grade") as string}`,
      file: `${formData.get("file") as string} ${formData.get("file") as string}`,
    };

    setFiles([...files, newFile]);
    setShowForm(false); // Switch back to table view
  };

  // Filter files based on search term
  const filteredFiles = files.filter((file) =>
    file.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
<div
  className={`p-5 shadow-lg rounded-lg h-[90vh] flex flex-col transition-all duration-300 ${
    showForm ? "bg-transparent" : "bg-purple-200"
  }`}
>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-black">
          {showForm ? "Add File" : "Manage File Access"}
        </h2>

        {!showForm && (
          <button
            className="bg-purple-500 text-white px-4 py-2 rounded-md hover:bg-purple-600"
            onClick={() => setShowForm(true)}
          >
            + Add File
          </button>
        )}
      </div>

      {/* Show Form if Adding a File */}
      {showForm ? (
        <form onSubmit={handleSubmit} className="bg-white p-5 rounded-lg shadow-lg w-full max-w-md mx-auto flex flex-col gap-4">
          <input type="text" name="username" placeholder="Username" required className="border p-2 rounded-md" />
          <input type="text" name="grade" placeholder="Grade" required className="border p-2 rounded-md" />
          <input type="text" name="filename" placeholder="File Name" required className="border p-2 rounded-md" />
          <input type="file" name="file" placeholder="File" required className="border p-2 rounded-md" />

          
          {/* Submit Button */}
          <button type="submit" className="bg-purple-500 text-white py-2 rounded-md hover:bg-purple-600">
            Upload
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
            <UploadTable files={filteredFiles} />
          </div>
        </>
      )}
    </div>
  );
};

export default UploadManagement;
