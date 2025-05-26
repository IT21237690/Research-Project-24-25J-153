const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const session = require("express-session");
require("dotenv").config();

const app = express();
const PORT = 7000;

// Middleware
app.use(cors({
  origin: "http://localhost:3001", // Your frontend URL
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

// Connect to MongoDB Atlas
console.log("Connecting to MongoDB Atlas...");
mongoose
  .connect('mongodb+srv://dbuser:dbuser123@researchproject.ojxgd.mongodb.net/rp_db?retryWrites=true&w=majority&appName=ResearchProject', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    serverSelectionTimeoutMS: 5000, // Timeout after 5s instead of 30s
    socketTimeoutMS: 45000, // Close sockets after 45s of inactivity
  })
  .then(() => console.log("Connected to MongoDB Atlas"))
  .catch((err) => {
    console.error("MongoDB connection error:", err);
    process.exit(1); // Exit if cannot connect to database
  });

// Add this to handle connection errors after initial connection
mongoose.connection.on('error', err => {
  console.error('MongoDB connection error:', err);
  // Don't exit here, just log the error
});

// Add this to handle when the connection is disconnected
mongoose.connection.on('disconnected', () => {
  console.log('MongoDB disconnected, trying to reconnect...');
});

// Add this to handle when the connection is reconnected
mongoose.connection.on('reconnected', () => {
  console.log('MongoDB reconnected');
});

// Routes
app.use("/api/videos", require("./routes/videos"));
app.use("/api/users", require("./routes/users"));
app.use("/api/recommendations", require("./routes/recommendations"));

// Simple route for testing
app.get("/", (req, res) => {
  res.send("YouTube Kids Recommendation API is running");
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});