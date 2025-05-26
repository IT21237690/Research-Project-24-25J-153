const express = require("express")
const router = express.Router()
const User = require("../models/user")
const axios = require("axios")

// Create a new user
router.post("/", async (req, res) => {
  try {
    const { username, age, interests } = req.body

    // Check if user already exists
    const existingUser = await User.findOne({ username })
    if (existingUser) {
      return res.status(400).json({ error: "Username already exists" })
    }

    const newUser = new User({
      username,
      age,
      interests: interests || [],
    })

    await newUser.save()
    res.status(201).json(newUser)
  } catch (error) {
    console.error("Error creating user:", error)
    res.status(500).json({ error: "Failed to create user" })
  }
})

// Get user watch history
router.get("/:username/history", async (req, res) => {
  try {
    const { username } = req.params

    console.log("Getting watch history for user:", username)

    const user = await User.findOne({ username })
    if (!user) {
      console.log("User not found:", username)
      return res.status(404).json({ error: "User not found" })
    }

    // Filter out any entries with undefined or null videoId
    const validWatchHistory = user.watchHistory.filter((item) => item.videoId)

    console.log(`Found ${validWatchHistory.length} valid watch history entries`)

    // Sort by most recent first
    const sortedHistory = validWatchHistory.sort(
      (a, b) => new Date(b.watchedAt).getTime() - new Date(a.watchedAt).getTime(),
    )

    res.json(sortedHistory)
  } catch (error) {
    console.error("Error getting watch history:", error)
    res.status(500).json({ error: "Failed to get watch history" })
  }
})

// Like a video
router.post("/:username/like/:videoId", async (req, res) => {
  try {
    const { username, videoId } = req.params

    const user = await User.findOne({ username })
    if (!user) {
      return res.status(404).json({ error: "User not found" })
    }

    if (!user.likedVideos.includes(videoId)) {
      user.likedVideos.push(videoId)
      await user.save()
    }

    res.status(200).json({ message: "Video liked successfully" })
  } catch (error) {
    console.error("Error liking video:", error)
    res.status(500).json({ error: "Failed to like video" })
  }
})

// Add video to watch history
router.post("/:username/history", async (req, res) => {
  try {
    const { username } = req.params
    const { videoId, title, watchDuration, completed } = req.body

    console.log("Adding to watch history:", username, { videoId, title, watchDuration, completed })

    if (!videoId || !title) {
      return res.status(400).json({ error: "VideoId and title are required" })
    }

    const user = await User.findOne({ username })
    if (!user) {
      console.error("User not found:", username)
      return res.status(404).json({ error: "User not found" })
    }

    // Check if video is already in watch history
    const existingIndex = user.watchHistory.findIndex((item) => item.videoId === videoId)

    if (existingIndex !== -1) {
      // Update existing entry
      console.log("Updating existing watch history entry")
      user.watchHistory[existingIndex] = {
        ...user.watchHistory[existingIndex],
        watchedAt: new Date(),
        watchDuration: Math.max(user.watchHistory[existingIndex].watchDuration || 0, watchDuration || 0),
        completed: completed || user.watchHistory[existingIndex].completed,
      }
    } else {
      // Add new entry
      console.log("Adding new watch history entry")
      user.watchHistory.push({
        videoId,
        title,
        watchDuration: watchDuration || 0,
        completed: completed || false,
        watchedAt: new Date(),
      })
    }

    const result = await user.save()
    console.log("Watch history updated for user:", username, "New count:", result.watchHistory.length)

    // Train the ML model if the user has at least 2 videos in watch history
    if (result.watchHistory.length >= 2) {
      try {
        console.log("Training ML model after watch history update")
        // Make this non-blocking so it doesn't slow down the response
        axios
          .post("http://localhost:7000/api/recommendations/train")
          .then(() => console.log("ML model training triggered successfully"))
          .catch((err) => console.error("Error triggering ML model training:", err))
      } catch (trainError) {
        console.error("Error training ML model:", trainError)
        // Don't fail the request if training fails
      }
    }

    res.status(200).json({
      message: "Watch history updated",
      watchHistoryCount: result.watchHistory.length,
    })
  } catch (error) {
    console.error("Error updating watch history:", error)
    res.status(500).json({ error: "Failed to update watch history", details: error.message })
  }
})

// Debug route to get user data
router.get("/:username/debug", async (req, res) => {
  try {
    const { username } = req.params

    const user = await User.findOne({ username })
    if (!user) {
      return res.status(404).json({ error: "User not found" })
    }

    res.json({
      username: user.username,
      age: user.age,
      interests: user.interests,
      watchHistoryCount: user.watchHistory.length,
      watchHistory: user.watchHistory,
      likedVideosCount: user.likedVideos.length,
      likedVideos: user.likedVideos,
    })
  } catch (error) {
    console.error("Error getting user debug data:", error)
    res.status(500).json({ error: "Failed to get user debug data" })
  }
})

// NEW: Check if KidsTube user exists
router.get("/kidstube-users/:username", async (req, res) => {
  try {
    const { username } = req.params

    console.log("Checking KidsTube user:", username)

    // Check if user exists in the User collection (KidsTube users)
    const user = await User.findOne({ username })

    if (user) {
      console.log("KidsTube user found:", username)
      res.status(200).json({
        exists: true,
        user: {
          username: user.username,
          age: user.age,
          interests: user.interests,
        },
      })
    } else {
      console.log("KidsTube user not found:", username)
      res.status(404).json({
        exists: false,
        message: "User not found in KidsTube",
      })
    }
  } catch (error) {
    console.error("Error checking KidsTube user:", error)
    res.status(500).json({ error: "Internal server error" })
  }
})

module.exports = router
