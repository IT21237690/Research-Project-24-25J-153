"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { checkKidsTubeUser } from "../services/api"

const Lobby: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [username, setUsername] = useState<string>("Student")
  const [isChecking, setIsChecking] = useState<boolean>(false)

  useEffect(() => {
    // Get username from URL parameters or localStorage
    const usernameFromUrl = searchParams.get("username")

    if (usernameFromUrl) {
      setUsername(usernameFromUrl)
      localStorage.setItem("username", usernameFromUrl)
      console.log("Lobby: Username from URL:", usernameFromUrl)
    } else {
      const storedUsername = localStorage.getItem("username")
      if (storedUsername) {
        setUsername(storedUsername)
        console.log("Lobby: Username from localStorage:", storedUsername)
      }
    }
  }, [searchParams])

  const handleWatchKidsTube = async () => {
    console.log("Lobby: Watch KidsTube clicked for user:", username)
    setIsChecking(true)

    try {
      console.log("Lobby: Calling checkKidsTubeUser...")
      const userExists = await checkKidsTubeUser(username)
      console.log("Lobby: User exists result:", userExists)

      if (userExists) {
        console.log("Lobby: Existing user - navigating to home")
        navigate("/home")
      } else {
        console.log("Lobby: New user - navigating to login")
        navigate("/login")
      }
    } catch (error) {
      console.error("Lobby: Error checking user:", error)
      // On error, assume new user and go to login
      console.log("Lobby: Error occurred - navigating to login")
      navigate("/login")
    } finally {
      setIsChecking(false)
    }
  }

  const handlePlayImageExplorer = () => {
    const usernameParam = encodeURIComponent(username)
    window.location.href = `http://localhost:3000/?username=${usernameParam}`
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 flex flex-col items-center justify-center p-4">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-blue-600 mb-4">Welcome to KidsZone, {username}!</h1>
        <p className="text-xl text-gray-600">Choose your adventure!</p>

        {/* Debug info */}
        {/* <div className="mt-4 p-2 bg-yellow-100 rounded text-sm">
          <p>Debug: Username = {username}</p>
          <p>Status: {isChecking ? "Checking user..." : "Ready"}</p>
        </div> */}
      </div>

      <div className="flex flex-col md:flex-row gap-8 w-full max-w-4xl">
        {/* Image Explorer Button */}
        <button
          onClick={handlePlayImageExplorer}
          className="flex-1 bg-gradient-to-r from-green-500 to-teal-400 hover:from-green-600 hover:to-teal-500 text-white rounded-xl p-8 shadow-lg transform transition-transform hover:scale-105 flex flex-col items-center justify-center"
        >
          <div className="text-5xl mb-4">🔍</div>
          <span className="text-2xl font-bold">Play Image Explorer 🔭</span>
          <p className="mt-4 text-sm opacity-90">Discover and learn with interactive images!</p>
        </button>

        {/* KidsTube Button */}
        <button
          onClick={handleWatchKidsTube}
          disabled={isChecking}
          className={`flex-1 bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white rounded-xl p-8 shadow-lg transform transition-transform hover:scale-105 flex flex-col items-center justify-center ${
            isChecking ? "opacity-50 cursor-not-allowed" : ""
          }`}
        >
          <div className="text-5xl mb-4">📺</div>
          <span className="text-2xl font-bold">{isChecking ? "Checking..." : "Watch KidsTube"}</span>
          <p className="mt-4 text-sm opacity-90">Enjoy educational videos made just for kids!</p>
        </button>
      </div>

      <div className="mt-16 text-center text-gray-500">
        <p>Safe, educational content for young explorers</p>
        <p className="text-sm mt-2">© 2023 KidsZone</p>
      </div>
    </div>
  )
}

export default Lobby
