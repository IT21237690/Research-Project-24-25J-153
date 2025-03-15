import React from "react";

const TeacherTable = ({ teachers }) => {
    
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
          {teachers.length > 0 ? (
            teachers.map((teacher) => (
              <tr key={teacher.id} className="text-center hover:bg-gray-100 overflow-y-auto">
                <td className="px-4 py-2 border">{teacher.id}</td>
                <td className="px-4 py-2 border">{teacher.name}</td>
                <td className="px-4 py-2 border">{teacher.subject}</td>
                <td className="px-4 py-2 border">{teacher.email}</td>
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

export default TeacherTable;
