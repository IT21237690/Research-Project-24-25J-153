import React from 'react';
import { Link } from 'react-router-dom';

interface VideoCardProps {
  video: any; // Using 'any' to handle different video structures
  onVideoSelect?: (videoId: string) => void;
}

const VideoCard: React.FC<VideoCardProps> = ({ video, onVideoSelect }) => {
  // Handle different video object structures
  let videoId: string;
  let title: string;
  let thumbnailUrl: string;
  let channelTitle: string;
  
  if (!video) {
    console.error('VideoCard received undefined or null video');
    return null; // Don't render anything if video is undefined
  }
  
  // Check if this is a YouTube API response format
  if (video.id && (typeof video.id === 'object' || typeof video.id === 'string')) {
    videoId = typeof video.id === 'string' ? video.id : video.id.videoId;
    
    if (video.snippet) {
      title = video.snippet.title;
      thumbnailUrl = video.snippet.thumbnails?.medium?.url || video.snippet.thumbnails?.default?.url;
      channelTitle = video.snippet.channelTitle;
    } else {
      title = video.title || 'Unknown Title';
      thumbnailUrl = video.thumbnailUrl || '/placeholder.svg';
      channelTitle = video.channelTitle || 'Unknown Channel';
    }
  } 
  // Check if this is our database format
  else if (video.videoId) {
    videoId = video.videoId;
    title = video.title || 'Unknown Title';
    thumbnailUrl = video.thumbnailUrl || '/placeholder.svg';
    channelTitle = video.channelTitle || 'Unknown Channel';
  }
  // Fallback for any other format
  else {
    console.error('Unknown video format:', video);
    videoId = 'unknown';
    title = 'Unknown Video';
    thumbnailUrl = '/placeholder.svg';
    channelTitle = 'Unknown Channel';
  }
  
  const handleClick = () => {
    if (onVideoSelect && videoId) {
      onVideoSelect(videoId);
    }
  };

  if (!videoId || videoId === 'unknown') {
    return null; // Don't render if we don't have a valid videoId
  }

  return (
    <div 
      className="video-card bg-white rounded-lg shadow-md overflow-hidden cursor-pointer transition-transform hover:scale-105"
      onClick={handleClick}
    >
      <Link to={`/video/${videoId}`}>
        <div className="relative">
          <img 
            src={thumbnailUrl || "/placeholder.svg"} 
            alt={title}
            className="w-full h-40 object-cover"
            onError={(e) => {
              // Fallback if image fails to load
              (e.target as HTMLImageElement).src = "/placeholder.svg";
            }}
          />
          <div className="absolute bottom-0 right-0 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded-tl-md">
            Kids
          </div>
        </div>
        <div className="p-3">
          <h3 className="text-sm font-medium line-clamp-2 mb-1">{title}</h3>
          <p className="text-xs text-gray-500">{channelTitle}</p>
        </div>
      </Link>
    </div>
  );
};

export default VideoCard;