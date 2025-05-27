import axios from "axios"

const API_BASE_URL = "http://20.193.146.113:7000/api"

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// Video API calls
export const searchVideos = async (query: string, maxResults = 10) => {
  const response = await api.get(`/videos/search`, {
    params: { query, maxResults },
  })
  return response.data
}

export const getVideoDetails = async (videoId: string) => {
  try {
    console.log("API call: getVideoDetails for", videoId)
    const response = await api.get(`/videos/${videoId}`)
    return response.data
  } catch (error) {
    console.error("Error in getVideoDetails:", error)
    throw error
  }
}

export const getRelatedVideos = async (videoId: string) => {
  const response = await api.get(`/videos/${videoId}/related`)
  return response.data
}

// User API calls
export const createUser = async (userData: { username: string; age: number; interests: string[] }) => {
  const response = await api.post("/users", userData)
  return response.data
}

export const addToWatchHistory = async (
  username: string,
  videoData: {
    videoId: string
    title: string
    watchDuration: number
    completed: boolean
  },
) => {
  try {
    console.log("Adding to watch history:", username, videoData)
    const response = await api.post(`/users/${username}/history`, videoData)
    return response.data
  } catch (error) {
    console.error("Error adding to watch history:", error)
    throw error
  }
}

export const likeVideo = async (username: string, videoId: string) => {
  const response = await api.post(`/users/${username}/like/${videoId}`)
  return response.data
}

export const getWatchHistory = async (username: string) => {
  try {
    console.log("Getting watch history for:", username)
    const response = await api.get(`/users/${username}/history`)
    return response.data
  } catch (error) {
    console.error("Error getting watch history:", error)
    throw error
  }
}

// Recommendation API calls
export const getRecommendations = async (username: string, count = 5, refresh = false) => {
  const response = await api.get(`/recommendations/${username}`, {
    params: {
      count,
      refresh: refresh.toString(),
    },
  })
  return response.data
}

export const trainRecommendationModel = async () => {
  const response = await api.post("/recommendations/train")
  return response.data
}

export const getUserDebug = async (username: string) => {
  try {
    const response = await api.get(`/users/${username}/debug`)
    return response.data
  } catch (error) {
    console.error("Error getting user debug data:", error)
    throw error
  }
}

// KidsTube specific API calls - FIXED PATH
export const checkKidsTubeUser = async (username: string): Promise<boolean> => {
  try {
    console.log("Frontend: Checking KidsTube user:", username)

    // FIXED: Changed from /kidstube-users/ to /users/kidstube-users/
    const response = await api.get(`/users/kidstube-users/${username}`)

    console.log("Frontend: KidsTube user check response:", response.status)

    if (response.status === 200) {
      console.log("Frontend: User exists in KidsTube")
      return true // User exists
    }

    return false // User doesn't exist
  } catch (error: any) {
    console.log("Frontend: Error checking KidsTube user:", error.response?.status)

    if (error.response && error.response.status === 404) {
      console.log("Frontend: User not found in KidsTube (404)")
      return false // User doesn't exist
    }

    console.error("Frontend: Unexpected error checking KidsTube user:", error)
    return false // Assume new user on error
  }
}

export default api
