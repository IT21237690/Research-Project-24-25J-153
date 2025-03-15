import React from "react";

const StudentTable = ({ students }) => {
    
  return (
    <div className=" bg-white  rounded-lg">
      <table className="w-full border-collapse">
        <thead className="sticky top-0 z-10">
          <tr className="bg-gray-200 sticky top-0">
            <th className="px-4 py-2 border">ID</th>
            <th className="px-4 py-2 border">Name</th>
            <th className="px-4 py-2 border">Subject</th>
            <th className="px-4 py-2 border">Email</th>
            
          </tr>
        </thead>
        <tbody>
          {students.length > 0 ? (
            students.map((student) => (
              <tr key={student.id} className="text-center hover:bg-gray-100 overflow-y-auto">
                <td className="px-4 py-2 border">{student.id}</td>
                <td className="px-4 py-2 border">{student.name}</td>
                <td className="px-4 py-2 border">{student.subject}</td>
                <td className="px-4 py-2 border">{student.email}</td>
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

export default StudentTable;
