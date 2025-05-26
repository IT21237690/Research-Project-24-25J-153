// cleanup-watch-history.js
const mongoose = require('mongoose');
require('dotenv').config();

// Connect to MongoDB
mongoose.connect('mongodb+srv://dbuser:dbuser123@researchproject.ojxgd.mongodb.net/rp_db?retryWrites=true&w=majority&appName=ResearchProject')
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

// Import User model
const User = require('./models/user');

async function cleanupWatchHistory() {
  try {
    console.log('Starting watch history cleanup...');
    
    // Find all users
    const users = await User.find();
    console.log(`Found ${users.length} users`);
    
    let totalFixed = 0;
    
    // Process each user
    for (const user of users) {
      console.log(`Processing user: ${user.username}`);
      
      // Count invalid entries
      const invalidEntries = user.watchHistory.filter(item => !item.videoId).length;
      console.log(`User has ${invalidEntries} invalid watch history entries`);
      
      if (invalidEntries > 0) {
        // Filter out invalid entries
        const validWatchHistory = user.watchHistory.filter(item => item.videoId);
        console.log(`Keeping ${validWatchHistory.length} valid entries`);
        
        // Update user
        user.watchHistory = validWatchHistory;
        await user.save();
        
        totalFixed += invalidEntries;
        console.log(`Fixed user ${user.username}`);
      }
    }
    
    console.log(`Cleanup complete. Fixed ${totalFixed} invalid watch history entries.`);
    process.exit(0);
  } catch (error) {
    console.error('Error during cleanup:', error);
    process.exit(1);
  }
}

cleanupWatchHistory();