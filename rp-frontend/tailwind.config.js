/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    fontFamily: {
      header: ["Literata, serif"],
      button:["Work Sans, sans-serif"]
    },
    extend: {
      backgroundImage: {
        'login-background': "url('../public/assets/Loginbg.jpg')", 
        'student-landing-background': "url('../public/assets/StudentLandingbg.jpg')", 
        'admin-landing-background': "url('../public/assets/AdminLandingbg.jpg')", 
        'fp-background': "url('../public/assets/FPbg.jpg')", 
        'qa-background': "url('../public/assets/QAbg.jpg')", 

      },
    },
  },
  plugins: [],
};
