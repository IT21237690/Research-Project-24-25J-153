const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const User = require('../models/user');
require('dotenv').config();

const router = express.Router();

router.post('/register', async (req, res) => {
  try {
    const { username, password, name } = req.body;
    
    const hashedPassword = await bcrypt.hash(password, 10);
  
    const newUser = new User({
      username,
      password: hashedPassword,
      name,
    });
  
    await newUser.save();
    res.status(201).json({ message: 'User registered successfully' });
  } catch (error) {
    console.error('Error occurred during registration:', error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    console.log(req.body);
    const user = await User.findOne({ username });

    if (!user) {
      return res.status(401).json({ message: 'User not found' });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    
    if (!isPasswordValid) {
      return res.status(401).json({ message: 'Incorrect password' });
    }

    const expiresIn = '1h';
    const tokenPayload = { username: user.username };
    const token = jwt.sign(tokenPayload, process.env.JWT_SECRET, { expiresIn });
    res.json({ token });
  } catch (error) {
    console.error('Error occurred during login:', error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
});




module.exports = router;
