import React, { useEffect, useState } from "react";
import SearchBar from "./SearchBar.tsx";
import UploadTable from "./Tables/UploadTable.tsx";

// Update the File interface to match your MongoDB model
interface FileData {
  file_name: string;
  file: string; // decoded text file content
  userid: string;
  uploaded_date: string;
}

const UploadManagement = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [files, setFiles] = useState<FileData[]>([]);

  // For demonstration, a fixed userId; in production this could be derived from auth context
  const userId = "34534534534534543";


  // Function to fetch files for the given user from the API
  const fetchFiles = () => {
    fetch(`http://127.0.0.1:8004/files/${userId}`, {
      headers: { "Content-Type": "application/json", accept: "application/json" },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch files");
        }
        return response.json();
      })
      .then((data) => {
        // Here we assume 'data' is an array of FileData objects.
        setFiles(data);
      })
      .catch((error) => {
        console.error("Error fetching files:", error);
      });
  };

  useEffect(() => {
    fetchFiles();
  }, [userId]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const formData = new FormData(e.currentTarget);
    const fileInput = e.currentTarget.file as HTMLInputElement;

    if (!fileInput.files?.length) {
      alert("Please select a file to upload.");
      return;
    }

    const file = fileInput.files[0];
    formData.append("file", file);

    try {
      const response = await fetch(`http://127.0.0.1:8004/upload_csv/${userId}`, {
        method: "POST",
        body: formData,
        headers: {
          accept: "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to upload file");
      }

      const result = await response.json();
      alert("File uploaded successfully!");

      // Re-fetch files after a successful upload to update the table
      fetchFiles();
      setShowForm(false); // Hide form after successful upload
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file. Please try again.");
    }
  };

  // Filter files based on search term (using file name)
  const filteredFiles = files.filter((file) =>
    file.file_name.toLowerCase().includes(searchTerm.toLowerCase())
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

      {showForm ? (
        <form
          onSubmit={handleSubmit}
          className="bg-white p-5 rounded-lg shadow-lg w-full max-w-md mx-auto flex flex-col gap-4"
        >
          <input
            type="file"
            name="file"
            placeholder="File"
            required
            className="border p-2 rounded-md"
          />
          <button
            type="submit"
            className="bg-purple-500 text-white py-2 rounded-md hover:bg-purple-600"
          >
            Upload
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
            <UploadTable files={filteredFiles} />
          </div>
        </>
      )}
    </div>
  );
};

export default UploadManagement;
