"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { createUser } from "../services/api"
import { useUser } from "../context/UserContext"

const Login: React.FC = () => {
  const [selectedInterests, setSelectedInterests] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [username, setUsername] = useState<string>("")
  const navigate = useNavigate()
  const { login } = useUser()

  // Kid-friendly categories
  const categories = [
    "Cartoons",
    "Animals",
    "Science",
    "Music",
    "Art",
    "Sports",
    "Cooking",
    "Nature",
    "Space",
    "Dinosaurs",
    "Cars",
    "Princesses",
    "Superheroes",
    "Magic",
    "Adventure",
    "Learning",
    "Stories",
    "Dance",
    "Games",
    "Crafts",
  ]

  useEffect(() => {
    // Get username from localStorage
    const storedUsername = localStorage.getItem("username") || "Student"
    setUsername(storedUsername)
  }, [])

  const toggleInterest = (interest: string) => {
    setSelectedInterests((prev) =>
      prev.includes(interest) ? prev.filter((item) => item !== interest) : [...prev, interest],
    )
  }

  const handleStartWatching = async (e: React.FormEvent) => {
    e.preventDefault()

    if (selectedInterests.length === 0) {
      setError("Please select at least one interest")
      return
    }

    try {
      const userData = {
        username,
        age: 8, // Default age
        interests: selectedInterests,
      }

      await createUser(userData)

      // Login the user
      login(username, userData.age, userData.interests)

      // Navigate to home page
      navigate("/home")
    } catch (err: any) {
      if (err.response && err.response.status === 400) {
        // If username already exists, just log in
        login(username, 8, selectedInterests)
        navigate("/home")
      } else {
        setError("Failed to create user account")
        console.error(err)
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-100 to-pink-100 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-purple-600 mb-2">Hi {username}! 👋</h1>
          <p className="text-2xl text-gray-700">What types of videos do you wanna see?</p>
        </div>

        <form onSubmit={handleStartWatching} className="space-y-6">
          {error && <div className="bg-red-100 text-red-700 p-3 rounded-md text-sm text-center">{error}</div>}

          {/* Categories Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {categories.map((category) => (
              <button
                key={category}
                type="button"
                onClick={() => toggleInterest(category)}
                className={`p-3 rounded-xl border-2 transition-all duration-200 text-sm font-medium ${
                  selectedInterests.includes(category)
                    ? "bg-purple-500 text-white border-purple-500 transform scale-105"
                    : "bg-white text-gray-700 border-gray-300 hover:border-purple-300 hover:bg-purple-50"
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          {/* Selected interests display */}
          {selectedInterests.length > 0 && (
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-purple-700 mb-2">You selected:</p>
              <div className="flex flex-wrap gap-2">
                {selectedInterests.map((interest) => (
                  <span key={interest} className="bg-purple-200 text-purple-800 px-3 py-1 rounded-full text-sm">
                    {interest}
                  </span>
                ))}
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={selectedInterests.length === 0}
            className={`w-full py-4 rounded-xl text-xl font-bold transition-all duration-200 ${
              selectedInterests.length > 0
                ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 transform hover:scale-105"
                : "bg-gray-300 text-gray-500 cursor-not-allowed"
            }`}
          >
            🎬 Start Watching!
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
