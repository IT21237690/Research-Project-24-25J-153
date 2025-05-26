const express = require("express")
const router = express.Router()
const Video = require("../models/video")
const youtubeService = require("../services/youtube-service")

// Get kids videos based on search query
router.get("/search", async (req, res) => {
  try {
    const { query = "kids educational", maxResults = 10 } = req.query
    const videos = await youtubeService.searchKidsVideos(query, maxResults)

    // Store videos in database for future reference
    for (const item of videos) {
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

    res.json(videos)
  } catch (error) {
    console.error("Error in search route:", error)
    res.status(500).json({ error: "Failed to search videos" })
  }
})

// Get video details
router.get('/:videoId', async (req, res) => {
  try {
    const { videoId } = req.params;
    console.log('Getting video details for:', videoId);
    
    // First, try to find the video in our database
    const videoFromDb = await Video.findOne({ videoId });
    
    if (videoFromDb) {
      console.log('Found video in database');
      // Convert to YouTube API format for consistency
      const response = {
        id: videoFromDb.videoId,
        snippet: {
          title: videoFromDb.title,
          description: videoFromDb.description,
          thumbnails: {
            default: { url: videoFromDb.thumbnailUrl },
            medium: { url: videoFromDb.thumbnailUrl },
            high: { url: videoFromDb.thumbnailUrl }
          },
          channelTitle: videoFromDb.channelTitle,
          publishedAt: videoFromDb.publishedAt
        }
      };
      return res.json(response);
    }
    
    // If not in database, fetch from YouTube API
    console.log('Fetching from YouTube API');
    const videoDetails = await youtubeService.getVideoDetails([videoId]);
    
    if (videoDetails && videoDetails.length > 0) {
      // Store in database for future
      const videoData = {
        videoId: videoId,
        title: videoDetails[0].snippet.title,
        description: videoDetails[0].snippet.description,
        thumbnailUrl: videoDetails[0].snippet.thumbnails.high.url,
        channelId: videoDetails[0].snippet.channelId,
        channelTitle: videoDetails[0].snippet.channelTitle,
        publishedAt: videoDetails[0].snippet.publishedAt
      };
      
      await Video.findOneAndUpdate(
        { videoId },
        videoData,
        { upsert: true, new: true }
      );
      
      return res.json(videoDetails[0]);
    }
    
    // If we get here, we couldn't find the video
    return res.status(404).json({ error: 'Video not found' });
  } catch (error) {
    console.error('Error in video details route:', error);
    res.status(500).json({ error: 'Failed to get video details' });
  }
});

// Get related videos
router.get("/:videoId/related", async (req, res) => {
  try {
    const { videoId } = req.params
    const relatedVideos = await youtubeService.getRelatedVideos(videoId)
    res.json(relatedVideos)
  } catch (error) {
    console.error("Error in related videos route:", error)
    res.status(500).json({ error: "Failed to get related videos" })
  }
})

module.exports = router

