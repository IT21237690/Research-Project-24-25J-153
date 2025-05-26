import React, { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { FaStar, FaStarHalfAlt, FaRegStar } from "react-icons/fa";
import { useSound } from "../../context/Sound.context.tsx";

const GetStars = ({ score, color }: { score: number; color: string }) => {
  const totalStars = 3;
  const filledStars = Math.floor(score * totalStars);
  const hasHalfStar = score * totalStars - filledStars >= 0.5;
  const emptyStars = totalStars - filledStars - (hasHalfStar ? 1 : 0);

  const soundRef = useRef<HTMLAudioElement>(null);
  const { soundEnabled } = useSound();

  useEffect(() => {
    if (soundEnabled && soundRef.current) {
      soundRef.current
        .play()
        .catch((err) => console.warn("Audio playback failed:", err));
    }
  }, [soundEnabled]);

  return (
    <div className="flex items-center justify-center space-x-5 text-8xl">
      <audio ref={soundRef} src="/sounds/shine.mp3" preload="auto" />

      {Array.from({ length: filledStars }).map((_, i) => (
        <motion.div
          key={`full-${i}`}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1.2, opacity: 1 }}
          transition={{ delay: i * 0.3, type: "spring", stiffness: 120 }}
        >
          <FaStar className={`text-${color}-500 drop-shadow-md`} />
        </motion.div>
      ))}

      {hasHalfStar && (
        <motion.div
          key="half"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1.2, opacity: 1 }}
          transition={{
            delay: filledStars * 0.3,
            type: "spring",
            stiffness: 120,
          }}
        >
          <FaStarHalfAlt className={`text-${color}-500 drop-shadow-md`} />
        </motion.div>
      )}

      {Array.from({ length: emptyStars }).map((_, i) => (
        <motion.div
          key={`empty-${i}`}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1.2, opacity: 1 }}
          transition={{
            delay: (filledStars + (hasHalfStar ? 1 : 0) + i) * 0.3,
            type: "spring",
            stiffness: 120,
          }}
        >
          <FaRegStar className="text-gray-400" />
        </motion.div>
      ))}
    </div>
  );
};

export default GetStars;
