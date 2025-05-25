import React, { useState } from "react";

const SearchBar = ({ onSearch }) => {
  const [searchTerm, setSearchTerm] = useState("");

  const handleChange = (e) => {
    setSearchTerm(e.target.value);
    onSearch(e.target.value);
  };

  return (
    <div className="mb-4">
      <input
        type="text"
        placeholder="Search teachers..."
        value={searchTerm}
        onChange={handleChange}
        className="border p-2 rounded-md w-full"
      />
    </div>
  );
};

export default SearchBar;
