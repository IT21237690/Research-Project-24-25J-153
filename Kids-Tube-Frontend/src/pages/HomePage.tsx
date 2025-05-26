"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { searchVideos, getRecommendations, getUserDebug } from "../services/api"
import VideoCard from "../components/VideoCard"
import { Search, RefreshCw } from "lucide-react"
import { useUser } from "../context/UserContext"

const HomePage: React.FC = () => {
  const { username } = useUser()
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [recommendedVideos, setRecommendedVideos] = useState<any[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [recommendationsLoading, setRecommendationsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [recommendationsError, setRecommendationsError] = useState<string | null>(null)
  const [showRecommendations, setShowRecommendations] = useState<boolean>(true)
  const [initialLoadDone, setInitialLoadDone] = useState<boolean>(false)
  const [userInterests, setUserInterests] = useState<string[]>([])
  const [isFirstTimeUser, setIsFirstTimeUser] = useState<boolean>(false)
  const navigate = useNavigate()

  // Fetch user data and check if first-time user
  useEffect(() => {
    if (username && !initialLoadDone) {
      checkUserAndFetchRecommendations()
    }
  }, [username, initialLoadDone])

  const checkUserAndFetchRecommendations = async () => {
    try {
      // Get user data including watch history and interests
      const userData = await getUserDebug(username)
      console.log("User data:", userData)

      // Check if user has watch history
      const isFirstTime = !userData.watchHistory || userData.watchHistory.length === 0
      setIsFirstTimeUser(isFirstTime)

      // Store user interests
      if (userData.interests && userData.interests.length > 0) {
        setUserInterests(userData.interests)
      }

      // Fetch recommendations based on whether it's a first-time user
      if (isFirstTime) {
        await fetchInterestBasedVideos(userData.interests)
      } else {
        await fetchRecommendations(false)
      }

      setInitialLoadDone(true)
    } catch (err) {
      console.error("Failed to check user status:", err)
      // Fall back to regular recommendations
      fetchRecommendations(false)
      setInitialLoadDone(true)
    }
  }

  const fetchInterestBasedVideos = async (interests: string[]) => {
    try {
      setRecommendationsLoading(true)
      setRecommendationsError(null)

      if (!interests || interests.length === 0) {
        console.log("No interests found, fetching regular recommendations")
        return fetchRecommendations(false)
      }

      console.log("Fetching videos based on interests:", interests)

      // Create a search query from user interests
      const interestsQuery = `${interests.join(" ")} kids educational`
      const results = await searchVideos(interestsQuery, 16)
      console.log("Interest-based videos:", results)

      setRecommendedVideos(results)
    } catch (err) {
      console.error("Failed to fetch interest-based videos:", err)
      setRecommendationsError("Failed to load videos based on your interests")
      // Fall back to regular recommendations
      fetchRecommendations(false)
    } finally {
      setRecommendationsLoading(false)
    }
  }

  const fetchRecommendations = async (refresh = false) => {
    try {
      setRecommendationsLoading(true)
      setRecommendationsError(null)
      console.log("Fetching recommendations for:", username, refresh ? "(refresh)" : "")

      // Pass refresh parameter to API
      const recommendations = await getRecommendations(username, 16, refresh)
      console.log("Received recommendations:", recommendations)

      // Don't shuffle the recommendations - keep them in the order returned by the API
      setRecommendedVideos(recommendations)
    } catch (err) {
      console.error("Failed to fetch recommendations:", err)
      setRecommendationsError("Failed to load recommendations")
    } finally {
      setRecommendationsLoading(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!searchQuery.trim()) return

    try {
      setLoading(true)
      setShowRecommendations(false)
      setError(null)

      // Add "kids" to the search query to filter for kid-friendly content
      const query = `${searchQuery} kids educational`
      console.log("Searching for:", query)
      const results = await searchVideos(query)
      console.log("Search results:", results)

      setSearchResults(results)
    } catch (err) {
      console.error("Failed to search videos:", err)
      setError("Failed to search videos")
    } finally {
      setLoading(false)
    }
  }

  const handleVideoSelect = (videoId: string) => {
    console.log("Selected video:", videoId)
    navigate(`/video/${videoId}`)
  }

  const handleClearSearch = () => {
    setSearchQuery("")
    setSearchResults([])
    setShowRecommendations(true)
  }

  const handleRefreshRecommendations = () => {
    // For first-time users, refresh with interest-based videos
    if (isFirstTimeUser && userInterests.length > 0) {
      fetchInterestBasedVideos(userInterests)
    } else {
      fetchRecommendations(true)
    }
  }

  // Determine the title to show based on user status
  const getRecommendationsTitle = () => {
    if (isFirstTimeUser) {
      return "Videos Based on Your Interests"
    }
    return "Recommended for You"
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for kids videos..."
              className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Search
          </button>
          {!showRecommendations && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Clear
            </button>
          )}
        </form>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, index) => (
            <div key={index} className="bg-gray-200 animate-pulse h-48 rounded-lg"></div>
          ))}
        </div>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : searchResults.length > 0 ? (
        <div>
          <h2 className="text-xl font-bold mb-4">Search Results</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {searchResults
              .filter((video) => video)
              .map((video, index) => (
                <VideoCard key={video.id || index} video={video} onVideoSelect={handleVideoSelect} />
              ))}
          </div>
        </div>
      ) : showRecommendations ? (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">{getRecommendationsTitle()}</h2>
            <button
              onClick={handleRefreshRecommendations}
              className="flex items-center text-blue-500 hover:text-blue-700"
              disabled={recommendationsLoading}
            >
              <RefreshCw size={16} className={`mr-1 ${recommendationsLoading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>

          {recommendationsLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {[...Array(16)].map((_, index) => (
                <div key={index} className="bg-gray-200 animate-pulse h-48 rounded-lg"></div>
              ))}
            </div>
          ) : recommendationsError ? (
            <div className="text-center p-8">
              <p className="text-red-500 mb-4">{recommendationsError}</p>
              <button
                onClick={handleRefreshRecommendations}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : recommendedVideos.length === 0 ? (
            <div className="text-center p-8 bg-gray-50 rounded-lg">
              <p className="text-gray-500 mb-2">No videos available yet.</p>
              <p className="text-sm text-gray-400 mb-4">
                {isFirstTimeUser
                  ? "We couldn't find videos matching your interests. Try refreshing or searching for specific topics."
                  : "Watch more videos to get personalized recommendations!"}
              </p>
              <button
                onClick={handleRefreshRecommendations}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Refresh
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {recommendedVideos
                .filter((video) => video)
                .map((video, index) => (
                  <VideoCard key={video.id || index} video={video} onVideoSelect={handleVideoSelect} />
                ))}
            </div>
          )}
        </div>
      ) : (
        <p className="text-center text-gray-500 my-12">No videos found. Try a different search term.</p>
      )}
    </div>
  )
}

export default HomePage

