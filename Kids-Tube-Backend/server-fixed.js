const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const session = require("express-session");
require("dotenv").config();

// Create Express app
const app = express();
const PORT = 7000;

// Middleware
app.use(cors({
  origin: "http://20.193.146.113:3001", // Your frontend URL
  credentials: true
}));
app.use(express.json());

// Add session support
app.use(session({
  secret: 'youtube-kids-recommendation-secret',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } // Set to true if using HTTPS
}));

// Simple route for testing
app.get("/", (req, res) => {
  res.send("YouTube Kids Recommendation API is running");
});

// Connect to MongoDB Atlas
console.log("Connecting to MongoDB Atlas...");
mongoose
  .connect('mongodb+srv://dbuser:dbuser123@researchproject.ojxgd.mongodb.net/rp_db?retryWrites=true&w=majority&appName=ResearchProject', {
    // Remove deprecated options
    serverSelectionTimeoutMS: 5000,
  })
  .then(() => {
    console.log("Connected to MongoDB Atlas");
    
    // Only register routes after successful DB connection
    // Routes
    app.use("/api/videos", require("./routes/videos"));
    app.use("/api/users", require("./routes/users"));
    app.use("/api/recommendations", require("./routes/recommendations"));
    
    // Start server
    const server = app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
    
    // Handle server shutdown gracefully
    process.on('SIGINT', () => {
      console.log('Shutting down server gracefully...');
      server.close(() => {
        mongoose.connection.close(false, () => {
          console.log('MongoDB connection closed.');
          process.exit(0);
        });
      });
    });
  })
  .catch((err) => {
    console.error("MongoDB connection error:", err);
    process.exit(1); // Exit if cannot connect to database
  });
