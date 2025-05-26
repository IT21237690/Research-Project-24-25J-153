/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  safelist: [
    'text-yellow-500',
    'text-cyan-500',
    'text-green-500',
    'text-pink-500',
  ],
  theme: {
    fontFamily: {
      header: ["Literata, serif"],
      button:["Work Sans, sans-serif"]
    },
    extend: {
      backgroundImage: {
        'main-landing-background': "url('../public/assets/MainLandingbg.jpg')", 
        'login-background': "url('../public/assets/Loginbg.jpg')", 
        'student-landing-background': "url('../public/assets/StudentLandingbg.jpg')", 
        'admin-landing-background': "url('../public/assets/AdminLandingbg.jpg')", 
        'fp-background': "url('../public/assets/FPbg.jpg')", 
        'qa-background': "url('../public/assets/QAbg.jpg')", 
        'student-profile-background': "url('../public/assets/StudentProfilebg.jpg')",
      },
    },
  },
  plugins: [],
};
