const express = require('express');
const cors = require('cors');
const { connectToDatabase } = require('./db connection'); 
const userRoutes = require('./routes/userRoutes');

const app = express();
const PORT = process.env.PORT || 5000;

// Connect to the database
connectToDatabase();

app.use(express.json());

// Use the cors middleware
app.use(cors());

// Use the authentication routes
app.use('/user', userRoutes);

const server = app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

module.exports = app;
