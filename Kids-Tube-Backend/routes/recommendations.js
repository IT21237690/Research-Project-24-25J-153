const express = require("express")
const router = express.Router()
const axios = require("axios")
const User = require("../models/user")
const Video = require("../models/video")
const youtubeService = require("../services/youtube-service")

const ML_ENGINE_URL = "http://127.0.0.1:5001"

// Get recommendations for a user
router.get("/:username", async (req, res) => {
  try {
    const { username } = req.params
    const { count = 16, refresh = "false" } = req.query

    // Check if user exists
    const user = await User.findOne({ username })
    if (!user) {
      return res.status(404).json({ error: "User not found" })
    }

    // Get user's watch history
    const watchedVideoIds = user.watchHistory.map((item) => item.videoId).filter(Boolean)

    // Get previously recommended videos from session if refresh is true
    let previouslyRecommended = []
    if (refresh === "true" && req.session && req.session.previousRecommendations) {
      previouslyRecommended = req.session.previousRecommendations[username] || []
    }

    // Combine watched videos and previously recommended videos to exclude
    const excludeVideos = [...watchedVideoIds, ...previouslyRecommended]

    // Check if user has any watch history - CHANGED FROM 3 TO 1
    const validWatchHistory = user.watchHistory.filter((item) => item.videoId && item.title)
    console.log(`User has ${validWatchHistory.length} valid videos in watch history`)

    // Store recommendations to prevent refreshing
    let cachedRecommendations = null

    // Check if we have cached recommendations and refresh is not requested
    if (
      refresh !== "true" &&
      req.session &&
      req.session.cachedRecommendations &&
      req.session.cachedRecommendations[username]
    ) {
      cachedRecommendations = req.session.cachedRecommendations[username]
      console.log("Using cached recommendations")
      return res.json(cachedRecommendations)
    }

    // Changed threshold from 3 to 1 - any watch history means they're not a first-time user
    if (validWatchHistory.length >= 1) {
      console.log("Returning user, using ML recommendation engine")

      // Train the model before getting recommendations
      console.log("Training ML model before getting recommendations")
      try {
        const users = await User.find()
        const videos = await Video.find()

        console.log(`Training ML model with ${users.length} users and ${videos.length} videos`)

        // Count users with valid watch history
        const usersWithHistory = users.filter((u) => u.watchHistory && u.watchHistory.some((h) => h.videoId && h.title))
        console.log(`${usersWithHistory.length} users have valid watch history`)

        // Train the model
        const trainResponse = await axios.post(`${ML_ENGINE_URL}/train`, {
          users,
          videos,
        })

        console.log("ML model training response:", trainResponse.data)
      } catch (trainError) {
        console.error("Error training ML model:", trainError.message)
      }

      // Get recommendations from ML engine with excluded videos
      try {
        const excludeParam = excludeVideos.join(",")
        const response = await axios.get(`${ML_ENGINE_URL}/recommend`, {
          params: {
            username,
            count,
            exclude: excludeParam,
          },
        })

        if (
          response.data.status === "success" &&
          response.data.recommendations &&
          response.data.recommendations.length > 0
        ) {
          console.log("ML engine returned recommendations:", response.data.recommendations)
          const videoIds = response.data.recommendations

          // Store these recommendations for future exclusion on refresh
          if (!req.session) req.session = {}
          if (!req.session.previousRecommendations) req.session.previousRecommendations = {}
          req.session.previousRecommendations[username] = videoIds

          // Get video details for the recommendations
          const recommendedVideos = await Video.find({ videoId: { $in: videoIds } })

          // If we found videos in our database
          if (recommendedVideos.length > 0) {
            // Sort videos in the same order as the recommendations
            const sortedVideos = videoIds
              .map((id) => recommendedVideos.find((video) => video.videoId === id))
              .filter(Boolean) // Remove any undefined entries

            // If we don't have enough videos, fetch more to fill the gap
            if (sortedVideos.length < count) {
              console.log(`Only found ${sortedVideos.length} videos out of ${count} requested, fetching more`)

              // Get IDs of videos we already have
              const existingIds = sortedVideos.map((video) => video.videoId)

              // Get additional videos that aren't in the recommendations or already watched
              const additionalVideos = await Video.find({
                videoId: {
                  $nin: [...existingIds, ...watchedVideoIds],
                },
              }).limit(count - sortedVideos.length)

              console.log(`Found ${additionalVideos.length} additional videos`)

              // Add the additional videos to our recommendations
              sortedVideos.push(...additionalVideos)
            }

            console.log("Returning ML recommendations:", sortedVideos.length)

            // Cache the recommendations
            if (!req.session) req.session = {}
            if (!req.session.cachedRecommendations) req.session.cachedRecommendations = {}
            req.session.cachedRecommendations[username] = sortedVideos

            return res.json(sortedVideos)
          }
        }

        // If ML engine doesn't have recommendations, fall back to simple recommendations
        console.log("ML engine didn't return usable recommendations, falling back")
        const fallbackRecommendations = await getFallbackRecommendations(user, count, excludeVideos)

        // Cache the recommendations
        if (!req.session) req.session = {}
        if (!req.session.cachedRecommendations) req.session.cachedRecommendations = {}
        req.session.cachedRecommendations[username] = fallbackRecommendations

        return res.json(fallbackRecommendations)
      } catch (mlError) {
        console.error("Error getting ML recommendations:", mlError.message)
        // Fall back to simple recommendations
        const fallbackRecommendations = await getFallbackRecommendations(user, count, excludeVideos)

        // Cache the recommendations
        if (!req.session) req.session = {}
        if (!req.session.cachedRecommendations) req.session.cachedRecommendations = {}
        req.session.cachedRecommendations[username] = fallbackRecommendations

        return res.json(fallbackRecommendations)
      }
    } else {
      // First-time user with no watch history
      console.log("First-time user with no watch history, fetching videos based on interests")

      // Check if user has interests
      if (user.interests && user.interests.length > 0) {
        console.log("User has interests:", user.interests)

        // Get videos based on user interests
        const interestBasedVideos = await getVideosBasedOnInterests(user.interests, count, excludeVideos)

        // Cache the recommendations
        if (!req.session) req.session = {}
        if (!req.session.cachedRecommendations) req.session.cachedRecommendations = {}
        req.session.cachedRecommendations[username] = interestBasedVideos

        return res.json(interestBasedVideos)
      } else {
        // No interests, get random videos
        console.log("User has no interests, fetching random kids videos")

        // Get random videos from YouTube API
        const randomVideos = await getRandomVideosForNewUser(count, excludeVideos)

        // Cache the recommendations
        if (!req.session) req.session = {}
        if (!req.session.cachedRecommendations) req.session.cachedRecommendations = {}
        req.session.cachedRecommendations[username] = randomVideos

        return res.json(randomVideos)
      }
    }
  } catch (error) {
    console.error("Error getting recommendations:", error)
    res.status(500).json({ error: "Failed to get recommendations" })
  }
})

// New function to get videos based on user interests
async function getVideosBasedOnInterests(interests, count, excludeVideos = []) {
  console.log(`Finding videos based on interests: ${interests.join(", ")}`)

  // Create regex patterns for each interest
  const interestPatterns = interests.map((interest) => new RegExp(interest, "i"))

  // Find videos that match any of the user's interests
  const interestVideos = await Video.find({
    $or: [
      { tags: { $in: interestPatterns } },
      { title: { $in: interestPatterns } },
      { description: { $in: interestPatterns } },
    ],
    videoId: { $nin: excludeVideos },
  }).limit(count * 2) // Get more than needed for variety

  console.log(`Found ${interestVideos.length} videos matching user interests`)

  // If we don't have enough videos, get some random ones to fill in
  if (interestVideos.length < count) {
    const remainingCount = count - interestVideos.length
    const existingIds = interestVideos.map((video) => video.videoId)

    console.log(`Getting ${remainingCount} additional random videos`)

    // Get random videos that don't match the ones we already have
    const randomVideos = await Video.aggregate([
      {
        $match: {
          videoId: { $nin: [...excludeVideos, ...existingIds] },
        },
      },
      { $sample: { size: remainingCount } },
    ])

    interestVideos.push(...randomVideos)
  }

  // Shuffle the videos for variety
  interestVideos.sort(() => Math.random() - 0.5)

  // Format videos for YouTube API compatibility if needed
  const formattedVideos = interestVideos.map((video) => {
    // Check if this is already in YouTube API format
    if (video.id && video.id.videoId) {
      return video
    }

    // Convert to YouTube API format
    return {
      id: { videoId: video.videoId },
      snippet: {
        title: video.title,
        description: video.description,
        thumbnails: {
          high: { url: video.thumbnailUrl },
          medium: { url: video.thumbnailUrl },
          default: { url: video.thumbnailUrl },
        },
        channelTitle: video.channelTitle,
        publishedAt: video.publishedAt,
      },
    }
  })

  return formattedVideos.slice(0, count)
}

// Train the recommendation model
router.post("/train", async (req, res) => {
  try {
    console.log("Training recommendation model...")

    const result = await trainMLModel()
    res.json(result || { status: "success", message: "Training initiated" })
  } catch (error) {
    console.error("Error training recommendation model:", error)
    res.status(500).json({ error: "Failed to train recommendation model" })
  }
})

// Function to train the ML model
async function trainMLModel() {
  // Get all users and videos from the database
  const users = await User.find()
  const videos = await Video.find()

  console.log(`Training ML model with ${users.length} users and ${videos.length} videos`)

  // Filter out users with no valid watch history
  const usersWithHistory = users.filter((user) => user.watchHistory.filter((item) => item.videoId).length > 0)

  console.log(`${usersWithHistory.length} users have valid watch history`)

  if (usersWithHistory.length === 0) {
    console.log("No users with valid watch history, skipping training")
    return
  }

  // Clean up user data before sending to ML engine
  const cleanUsers = usersWithHistory.map((user) => ({
    username: user.username,
    watchHistory: user.watchHistory.filter((item) => item.videoId),
    likedVideos: user.likedVideos || [],
  }))

  // Send data to ML engine for training
  const response = await axios.post(`${ML_ENGINE_URL}/train`, {
    users: cleanUsers,
    videos,
  })

  console.log("ML model training response:", response.data)
  return response.data
}

// Update the fallback recommendation function to exclude specific videos
async function getFallbackRecommendations(user, count, excludeVideos = []) {
  // Get user's interests
  const interests = user.interests || []

  // Get user's watch history
  const watchedVideoIds = user.watchHistory.map((item) => item.videoId)

  // Combine watched videos and excluded videos
  const allExcludedIds = [...new Set([...watchedVideoIds, ...excludeVideos])]

  // Find videos that match user's interests and haven't been watched
  const query = {}

  if (interests.length > 0) {
    // Search for videos with matching tags or titles
    const interestRegex = interests.map((interest) => new RegExp(interest, "i"))
    query.$or = [{ tags: { $in: interestRegex } }, { title: { $in: interestRegex } }]
  }

  // Exclude already watched videos and other excluded videos
  if (allExcludedIds.length > 0) {
    query.videoId = { $nin: allExcludedIds }
  }

  // Get recommendations with randomness - fetch more than needed
  const recommendations = await Video.aggregate([
    { $match: query },
    { $sample: { size: Number.parseInt(count) * 2 } }, // Get twice as many for variety
  ])

  // Shuffle the results
  recommendations.sort(() => Math.random() - 0.5)

  // If not enough recommendations, get random popular videos
  if (recommendations.length < count) {
    const remainingCount = count - recommendations.length
    const recommendedIds = recommendations.map((video) => video.videoId)
    const excludeIds = [...allExcludedIds, ...recommendedIds]

    const popularVideos = await Video.aggregate([
      { $match: { videoId: { $nin: excludeIds } } },
      { $sample: { size: remainingCount * 2 } }, // Get twice as many for variety
    ])

    // Shuffle the popular videos
    popularVideos.sort(() => Math.random() - 0.5)

    recommendations.push(...popularVideos)
  }

  // Return only the requested number of videos
  return recommendations.slice(0, count)
}

// Function to get random videos for new users
async function getRandomVideosForNewUser(count, excludeVideos = []) {
  // List of kid-friendly search terms
  const searchTerms = [
    "kids educational",
    "kids cartoons",
    "children learning",
    "kids animals",
    "kids science",
    "educational animation",
    "kids nature",
    "kids math",
    "children stories",
    "kids music",
    "kids crafts",
    "kids games",
    "kids experiments",
    "kids dinosaurs",
    "kids space",
  ]

  // Pick multiple random search terms to ensure variety
  const numTerms = Math.min(3, searchTerms.length)
  const selectedTerms = []

  for (let i = 0; i < numTerms; i++) {
    const randomIndex = Math.floor(Math.random() * searchTerms.length)
    selectedTerms.push(searchTerms[randomIndex])
    searchTerms.splice(randomIndex, 1) // Remove the term to avoid duplicates
  }

  const allVideos = []

  // Fetch videos for each selected term
  for (const term of selectedTerms) {
    console.log(`Fetching random kids videos with search term: ${term}`)

    try {
      // Search for videos using the YouTube API
      const youtubeService = require("../services/youtube-service")
      const videos = await youtubeService.searchKidsVideos(term, Math.ceil(count / numTerms))

      // Filter out any excluded videos
      const filteredVideos = videos.filter((video) => !excludeVideos.includes(video.id.videoId))

      allVideos.push(...filteredVideos)

      // Store videos in database for future reference
      for (const item of filteredVideos) {
        const videoData = {
          videoId: item.id.videoId,
          title: item.snippet.title,
          description: item.snippet.description,
          thumbnailUrl: item.snippet.thumbnails.high.url,
          channelId: item.snippet.channelId,
          channelTitle: item.snippet.channelTitle,
          publishedAt: item.snippet.publishedAt,
        }

        // Use findOneAndUpdate with upsert to avoid duplicates
        await Video.findOneAndUpdate({ videoId: videoData.videoId }, videoData, { upsert: true, new: true })
      }
    } catch (error) {
      console.error(`Error fetching random videos for term ${term}:`, error)
    }
  }

  console.log(`Fetched a total of ${allVideos.length} videos from YouTube API`)

  // Shuffle the videos
  allVideos.sort(() => Math.random() - 0.5)

  // If we don't have enough videos, fall back to database
  if (allVideos.length < count) {
    console.log("Not enough videos from YouTube API, falling back to database")

    const remainingCount = count - allVideos.length
    const existingIds = allVideos.map((video) => video.id.videoId)

    const randomVideos = await Video.aggregate([
      { $match: { videoId: { $nin: [...excludeVideos, ...existingIds] } } },
      { $sample: { size: remainingCount } },
    ])

    // Convert database videos to the same format as YouTube API videos
    const formattedDbVideos = randomVideos.map((video) => ({
      id: { videoId: video.videoId },
      snippet: {
        title: video.title,
        description: video.description,
        thumbnails: {
          high: { url: video.thumbnailUrl },
          medium: { url: video.thumbnailUrl },
          default: { url: video.thumbnailUrl },
        },
        channelTitle: video.channelTitle,
        publishedAt: video.publishedAt,
      },
    }))

    allVideos.push(...formattedDbVideos)
  }

  // Return only the requested number of videos
  return allVideos.slice(0, count)
}

// Function to get random YouTube videos
async function getRandomYouTubeVideos(res, count) {
  try {
    // Fetch random kids videos from YouTube API
    const youtubeVideos = await youtubeService.getRandomKidsVideos(count)
    console.log(`Fetched ${youtubeVideos.length} random kids videos from YouTube API`)

    // Store videos in database for future reference
    const storedVideos = []

    for (const item of youtubeVideos) {
      const videoData = {
        videoId: item.id.videoId,
        title: item.snippet.title,
        description: item.snippet.description,
        thumbnailUrl: item.snippet.thumbnails.high.url,
        channelId: item.snippet.channelId,
        channelTitle: item.snippet.channelTitle,
        publishedAt: item.snippet.publishedAt,
        tags: ["kids", "educational"], // Default tags
        category: "Education", // Default category
        viewCount: Math.floor(Math.random() * 1000) + 100, // Random view count
      }

      // Use findOneAndUpdate with upsert to avoid duplicates
      const storedVideo = await Video.findOneAndUpdate({ videoId: videoData.videoId }, videoData, {
        upsert: true,
        new: true,
      })

      storedVideos.push(storedVideo)
    }

    console.log(`Stored ${storedVideos.length} videos in database`)
    return res.json(storedVideos)
  } catch (error) {
    console.error("Error getting random YouTube videos:", error)
    return res.json([])
  }
}

// Content-based recommendation function
async function getContentBasedRecommendations(user, count) {
  console.log("Using content-based recommendation system")

  // Get user's watch history
  const watchedVideoIds = user.watchHistory
    .filter((item) => item.videoId) // Filter out undefined videoIds
    .map((item) => item.videoId)

  if (watchedVideoIds.length === 0) {
    return []
  }

  // Get the most recently watched videos (up to 3)
  const recentWatchHistory = user.watchHistory
    .filter((item) => item.videoId) // Filter out undefined videoIds
    .sort((a, b) => new Date(b.watchedAt) - new Date(a.watchedAt))
    .slice(0, 3)

  const recentVideoIds = recentWatchHistory.map((item) => item.videoId)
  console.log("Recent video IDs:", recentVideoIds)

  // Get videos similar to recently watched videos
  const recentVideos = await Video.find({ videoId: { $in: recentVideoIds } })

  if (recentVideos.length === 0) {
    return []
  }

  // Extract tags and categories from recent videos
  const tags = recentVideos.flatMap((video) => video.tags || [])
  const categories = recentVideos.map((video) => video.category).filter(Boolean)

  console.log("Tags from recent videos:", tags)
  console.log("Categories from recent videos:", categories)

  // Find videos with similar tags or categories
  const query = {
    videoId: { $nin: watchedVideoIds }, // Exclude already watched videos
    $or: [],
  }

  if (tags.length > 0) {
    query.$or.push({ tags: { $in: tags } })
  }

  if (categories.length > 0) {
    query.$or.push({ category: { $in: categories } })
  }

  // If we don't have any criteria, return empty array
  if (query.$or.length === 0) {
    return []
  }

  // Find similar videos
  const similarVideos = await Video.find(query).limit(Number.parseInt(count))

  return similarVideos
}

module.exports = router

