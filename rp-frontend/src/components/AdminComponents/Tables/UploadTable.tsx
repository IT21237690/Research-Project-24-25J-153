import React from "react";

const UploadTable = ({ files }) => {
    
  return (
    <div className=" bg-white  rounded-lg">
      <table className="w-full border-collapse">
        <thead className="sticky top-0 z-10">
          <tr className="bg-gray-200 sticky top-0">
            <th className="px-4 py-2 border">ID</th>
            <th className="px-4 py-2 border">File Name</th>
            <th className="px-4 py-2 border">Grade</th>
            <th className="px-4 py-2 border">User Name</th>
            <th className="px-4 py-2 border">File</th>

          </tr>
        </thead>
        <tbody>
          {files.length > 0 ? (
            files.map((file) => (
              <tr key={file.id} className="text-center hover:bg-gray-100 overflow-y-auto">
                <td className="px-4 py-2 border">{file.id}</td>
                <td className="px-4 py-2 border">{file.filename}</td>
                <td className="px-4 py-2 border">{file.username}</td>
                <td className="px-4 py-2 border">{file.grade}</td>
                <td className="px-4 py-2 border">{file.file}</td>

              </tr>
            ))
          ) : (
            <tr>
              <td  className="text-center py-4 text-gray-500">
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
