const mongoose = require('mongoose');
//const User = require('./models/user');
require('dotenv').config();


function connectToDatabase() {
  return new Promise((resolve, reject) => {
    mongoose.connect(process.env.DB_URI, {
     
    })
    .then(() => {
      console.log('Connected to the database');
      resolve();
    })
    .catch(error => {
      console.error('Error connecting to the database:', error.message);
      reject(error);
    });
  });
}



module.exports = { connectToDatabase };
