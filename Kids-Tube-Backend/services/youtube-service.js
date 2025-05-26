const { google } = require("googleapis")
require("dotenv").config()

const youtube = google.youtube({
  version: "v3",
  auth: 'AIzaSyC1nCeWhmO_6L8eIiE2mfQYX3zXjhE-UBQ',
})

// Function to search for kids content
async function searchKidsVideos(query = "kids educational", maxResults = 10) {
  try {
    const response = await youtube.search.list({
      part: "snippet",
      q: query,
      maxResults,
      type: "video",
      videoCategoryId: "1", // Film & Animation - often contains cartoons
      safeSearch: "strict", // Enforce safe search
      // Add relevantLanguage if you want to filter by language
    })

    return response.data.items
  } catch (error) {
    console.error("Error searching YouTube:", error)
    throw error
  }
}

// Function to get video details
async function getVideoDetails(videoIds) {
  try {
    const response = await youtube.videos.list({
      part: "snippet,contentDetails,statistics",
      id: videoIds.join(","),
    })

    return response.data.items
  } catch (error) {
    console.error("Error getting video details:", error)
    throw error
  }
}

// Function to get related videos
async function getRelatedVideos(videoId, maxResults = 10) {
  try {
    const response = await youtube.search.list({
      part: "snippet",
      relatedToVideoId: videoId,
      type: "video",
      maxResults,
      safeSearch: "strict",
    })

    return response.data.items
  } catch (error) {
    console.error("Error getting related videos:", error)
    throw error
  }
}

// Function to get random kids videos
async function getRandomKidsVideos(maxResults = 10) {
  try {
    // List of kid-friendly search terms
    const kidSearchTerms = [
      'kids educational',
      'children learning',
      'kids cartoons',
      'educational animation',
      'kids science',
      'children stories',
      'kids math',
      'kids music',
      'kids animals',
      'kids nature'
    ];
    
    // Pick a random search term
    const randomTerm = kidSearchTerms[Math.floor(Math.random() * kidSearchTerms.length)];
    
    console.log(`Fetching random kids videos with search term: ${randomTerm}`);
    
    const response = await youtube.search.list({
      part: 'snippet',
      q: randomTerm,
      maxResults,
      type: 'video',
      videoCategoryId: '1', // Film & Animation - often contains cartoons
      safeSearch: 'strict', // Enforce safe search
      relevanceLanguage: 'en' // English content
    });
    
    return response.data.items;
  } catch (error) {
    console.error('Error getting random kids videos:', error);
    throw error;
  }
}

// Export the new function
module.exports = {
  searchKidsVideos,
  getVideoDetails,
  getRelatedVideos,
  getRandomKidsVideos
};

