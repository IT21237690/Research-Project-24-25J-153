// import React from "react";
// import { useState } from "react";
// import { Link, useNavigate } from 'react-router-dom';
// import Header from "../components/Header.tsx";
// function Registration({ onRegister }) {
//   const [username, setUsername] = useState("");
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState("");
//   const navigate = useNavigate();

//   const handleSubmit = async (e) => {

//   };

//   return (
//     // <div className="registration-container">
//     //   <div className="registration-card">
//     //     <h2 className="registration-heading">Register</h2>
//     //     <form onSubmit={handleSubmit} className="registration-form">
//     //       <div className="form-group">
//     //         <label htmlFor="username" className="form-label">
//     //           Username
//     //         </label>
//     //         <input
//     //           type="text"
//     //           id="username"
//     //           className="form-input"
//     //           placeholder="Enter your username"
//     //           value={username}
//     //           onChange={(e) => setUsername(e.target.value)}
//     //         />
//     //       </div>
//     //       <div className="form-group">
//     //         <label htmlFor="email" className="form-label">
//     //           Email
//     //         </label>
//     //         <input
//     //           type="email"
//     //           id="email"
//     //           className="form-input"
//     //           placeholder="Enter your email"
//     //           value={email}
//     //           onChange={(e) => setEmail(e.target.value)}
//     //         />
//     //       </div>
//     //       <div className="form-group">
//     //         <label htmlFor="password" className="form-label">
//     //           Password
//     //         </label>
//     //         <input
//     //           type="password"
//     //           id="password"
//     //           className="form-input"
//     //           placeholder="Enter your password"
//     //           value={password}
//     //           onChange={(e) => setPassword(e.target.value)}
//     //         />
//     //       </div>
//     //       <button type="submit" className="registration-btn" disabled={isLoading}>
//     //         {isLoading ? "Registering..." : "Register"}
//     //       </button>
//     //     </form>
//     //     {error && <p className="error-msg">{error}</p>}
       
//     //     <p className="login-link">Already have an account? <Link to="/" className="login-link">Login</Link></p>
//     //   </div>
//     // </div>
//     <div className="flex flex-col h-screen">
//     {/* <Header /> */}

//     {/* Main Content */}
//     <div className="flex-1 flex justify-center items-center bg-login-background bg-cover bg-center">
//       {/* Login Box */}
//       <div
//         className="bg-slate-300 border-4 border-dashed border-teal-500 
//                   px-8 py-10 w-full max-w-md rounded-lg shadow-lg flex flex-col items-center"
//       >
//         {/* Login Title */}
//         <h2 className="text-2xl font-bold mb-4">SIGNUP</h2>

//         {/* Login Form */}
//         <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
       
//         </form>
//       </div>
//     </div>
//   </div>

//   );
// }

// export default Registration;


// // add
// // fn, ln, un, pw, email, grade, role