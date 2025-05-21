import { FaStar, FaStarHalfAlt, FaRegStar } from "react-icons/fa";
import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import React from "react";
import { useSound } from "../../context/Sound.context.tsx";

const RenderStars = ({ similarity, userAnswer, correctAnswer }) => {
  const clickSoundRef = useRef<HTMLAudioElement>(null);
  const soundRef = useRef<HTMLAudioElement>(null);
  const { soundEnabled } = useSound();

  const handleNext = () => {
    if (soundEnabled && clickSoundRef.current) {
      clickSoundRef.current.play().catch((err) =>
        console.warn("Click sound failed:", err)
      );
    }
  
    setTimeout(() => {
      window.location.reload();
    }, 300); // Wait to let the sound play
  };
  
  useEffect(() => {
    if (soundEnabled && soundRef.current) {
      soundRef.current.play().catch((err) =>
        console.warn("Initial sound failed:", err)
      );
    }
  }, [soundEnabled]); 
  if (similarity === null) return null; // Avoid running the rest of the component if similarity is null

  // Convert similarity (0-1) to a 0-3 star rating
  const totalStars = 3;
  const starRating = similarity * totalStars;
  const fullStars = Math.floor(starRating); // Number of full stars
  const hasHalfStar = starRating - fullStars >= 0.5; // Check for half-star
  const emptyStars = totalStars - fullStars - (hasHalfStar ? 1 : 0); // Remaining empty stars

  return (
    <div className="flex flex-col items-center bg-white/30 text-white rounded-lg shadow-md p-6 mt-5 backdrop-blur-lg">
      <h2 className="text-2xl font-extrabold text-pink-400">
        Your Answer and Correct Answer
      </h2>

      <p className="text-gray-900 mt-4 text-xl font-semibold">
        <strong>Your Answer:</strong> {userAnswer}
      </p>
      <p className="text-gray-900 text-xl font-semibold">
        <strong>Correct Answer:</strong> {correctAnswer}
      </p>

      {/* Star Display */}
      <div className="flex space-x-5 text-8xl mt-6">
        <audio ref={soundRef} src="/sounds/shine.mp3" preload="auto" />
        <audio ref={clickSoundRef} src="/sounds/generalButtonClick.mp3" preload="auto" />

        {/* Animated Full Stars */}
        {Array.from({ length: fullStars }).map((_, index) => (
          <motion.div
            key={`full-${index}`}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1.2, opacity: 1 }}
            transition={{
              delay: index * 0.3,
              type: "spring",
              stiffness: 120,
            }}
          >
            <FaStar className="text-yellow-500 drop-shadow-md" />
          </motion.div>
        ))}

        {/* Animated Half Star */}
        {hasHalfStar && (
          <motion.div
            key="half"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1.2, opacity: 1 }}
            transition={{
              delay: fullStars * 0.3,
              type: "spring",
              stiffness: 120,
            }}
          >
            <FaStarHalfAlt className="text-yellow-500 drop-shadow-md" />
          </motion.div>
        )}

        {/* Animated Empty Stars */}
        {Array.from({ length: emptyStars }).map((_, index) => (
          <motion.div
            key={`empty-${index}`}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1.2, opacity: 1 }}
            transition={{
              delay: (fullStars + (hasHalfStar ? 1 : 0) + index) * 0.3,
              type: "spring",
              stiffness: 120,
            }}
          >
            <FaRegStar className="text-gray-400" />
          </motion.div>
        ))}
      </div>

      {/* Feedback Message */}
      <p className="text-xl font-bold mt-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-pink-400 animate-gradient-text hover:scale-105 transition-all text-5xl">
        {similarity <= 0.2
          ? "Nice try! Keep practicing!"
          : similarity <= 0.5
          ? "Good job! Almost there!"
          : "Excellent! Well done!"}
      </p>

      {/* Next Button */}
      <button
        onClick={handleNext}
        className="mt-6 bg-gradient-to-r from-pink-400 via-pink-500 to-pink-600 text-white text-xl font-bold py-4 px-8 rounded-lg shadow-xl hover:scale-110 transform transition duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-pink-300 focus:ring-offset-2"
      >
        Next
      </button>
    </div>
  );
};

export default RenderStars;
