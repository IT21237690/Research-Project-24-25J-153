import React from "react";

const UploadTable = ({ files }) => {
  // Function to handle downloading the CSV file
  const handleDownload = (base64Content, fileName) => {
    // Decode the base64 string into binary data
    const byteCharacters = atob(base64Content);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);

    // Create a blob from the binary data with CSV MIME type
    const blob = new Blob([byteArray], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    // Create a temporary link and trigger the download
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-lg">
      <table className="w-full border-collapse">
        <thead className="sticky top-0 z-10">
          <tr className="bg-gray-200 sticky top-0">
            <th className="px-4 py-2 border">File Name</th>
            <th className="px-4 py-2 border">Uploaded Date</th>
            <th className="px-4 py-2 border">Action</th>
          </tr>
        </thead>
        <tbody>
          {files.length > 0 ? (
            files.map((file, index) => (
              <tr key={file.id || index} className="text-center hover:bg-gray-100">
                <td className="px-4 py-2 border">{file.file_name}</td>
                <td className="px-4 py-2 border">
                  {new Date(file.uploaded_date).toLocaleString()}
                </td>
                <td className="px-4 py-2 border">
                  <button
                    className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
                    onClick={() => handleDownload(file.file, file.file_name)}
                  >
                    Download CSV
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td className="text-center py-4 text-gray-500" colSpan={3}>
                No data available
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default UploadTable;