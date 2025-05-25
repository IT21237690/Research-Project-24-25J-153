import React, { useState } from "react";
import { FaStar, FaStarHalfAlt, FaRegStar } from "react-icons/fa"; // Import star icons

// Function to convert score (0-1) to stars (max 3 stars)
const renderStars = (score) => {
  const maxStars = 3;
  const starRating = score * maxStars; // Convert score to 3-star scale
  const fullStars = Math.floor(starRating);
  const hasHalfStar = starRating - fullStars >= 0.5;

  return (
    <span className="flex justify-center">
      {[...Array(maxStars)].map((_, index) => (
        <span key={index} className="text-yellow-400 text-xl">
          {index < fullStars ? <FaStar /> : hasHalfStar && index === fullStars ? <FaStarHalfAlt /> : <FaRegStar />}
        </span>
      ))}
    </span>
  );
};

const ResultsTable = ({ headers, data }) => {
  const rowsPerPage = 3;
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(data.length / rowsPerPage);
  const startIdx = (currentPage - 1) * rowsPerPage;
  const paginatedData = data.slice(startIdx, startIdx + rowsPerPage);

  return (
    <div className="flex flex-col w-full h-80">
      {/* Fixed Height Table Container */}
      <div className="h-96 border border-gray-300 rounded-md shadow-md overflow-y-auto">
        <table className="w-full border-collapse h-full">
          {/* Table Header */}
          <thead className="bg-blue-500 text-white">
            <tr>
              {headers.map((header, index) => (
                <th key={index} className="p-2 border border-gray-300">
                  {header}
                </th>
              ))}
            </tr>
          </thead>

          {/* Table Body with Fixed Row Heights */}
          <tbody className="h-52">
            {paginatedData.length > 0 ? (
              paginatedData.map((row, rowIndex) => (
                <tr key={rowIndex} className="text-center border border-gray-300 h-2">
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex} className="p-4 border border-gray-300">
                      {/* Check if it's a score column and convert it to stars */}
                      {typeof cell === "number" && cell >= 0 && cell <= 1 ? renderStars(cell) : cell}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr className="h-2">
                <td colSpan={headers.length} className="text-center p-4">
                  No data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {paginatedData.length > 0 && (
        <div className="flex justify-between items-center mt-4">
          <button
            className="px-4 py-2 bg-gray-200 rounded-md disabled:opacity-50"
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <span className="font-semibold">
            Page {currentPage} of {totalPages}
          </span>
          <button
            className="px-4 py-2 bg-gray-200 rounded-md disabled:opacity-50"
            onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default ResultsTable;
