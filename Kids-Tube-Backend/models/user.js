const mongoose = require("mongoose")

const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    unique: true,
  },
  age: {
    type: Number,
    required: true,
  },
  interests: [String],
  watchHistory: [
    {
      videoId: String,
      title: String,
      watchedAt: {
        type: Date,
        default: Date.now,
      },
      watchDuration: Number, // in seconds
      completed: Boolean,
    },
  ],
  likedVideos: [String], // Array of video IDs
  createdAt: {
    type: Date,
    default: Date.now,
  },
})

module.exports = mongoose.model("User", userSchema, "KidsTubeUsers")

// module.exports = mongoose.model("User", userSchema)