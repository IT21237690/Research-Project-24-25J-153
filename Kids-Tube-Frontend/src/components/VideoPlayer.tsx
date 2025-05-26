import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getVideoDetails, addToWatchHistory, likeVideo } from '../services/api';
import { ThumbsUp, ArrowLeft } from 'lucide-react';

interface VideoPlayerProps {
  username: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ username }) => {
  const { videoId } = useParams<{ videoId: string }>();
  const [videoDetails, setVideoDetails] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [liked, setLiked] = useState<boolean>(false);
  const [watchStartTime, setWatchStartTime] = useState<number>(0);
  const [watchRecorded, setWatchRecorded] = useState<boolean>(false);
  const navigate = useNavigate();

  // Fetch video details when component mounts
  useEffect(() => {
    const fetchVideoDetails = async () => {
      try {
        setLoading(true);
        console.log('Fetching video details for:', videoId);
        
        if (!videoId) {
          throw new Error('Video ID is missing');
        }
        
        try {
          const details = await getVideoDetails(videoId);
          console.log('Video details:', details);
          setVideoDetails(details);
        } catch (err) {
          console.error('Error fetching from API, using fallback:', err);
          // Fallback: Create a minimal video details object
          setVideoDetails({
            id: videoId,
            snippet: {
              title: 'YouTube Video',
              channelTitle: 'YouTube Channel',
              description: 'Video description not available'
            }
          });
        }
        
        setWatchStartTime(Date.now());
      } catch (err) {
        console.error('Error in video player:', err);
        setError('Failed to load video. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (videoId) {
      fetchVideoDetails();
    }
  }, [videoId]);

  // Record watch history after a certain amount of time
  useEffect(() => {
    // Only proceed if we have all required data and haven't recorded yet
    if (!videoId || !username || watchStartTime === 0 || watchRecorded) return;

    // Record watch after 10 seconds
    const timer = setTimeout(() => {
      const watchDuration = Math.floor((Date.now() - watchStartTime) / 1000);
      const videoTitle = videoDetails?.snippet?.title || 'Unknown Video';
      
      // Double-check that videoId is valid before recording
      if (!videoId) {
        console.error('Attempted to record watch history with undefined videoId');
        return;
      }
      
      console.log('Recording watch history after 10 seconds:', {
        username,
        videoId,
        title: videoTitle,
        watchDuration,
        completed: false
      });
      
      addToWatchHistory(username, {
        videoId: videoId,
        title: videoTitle,
        watchDuration,
        completed: false
      })
      .then(() => {
        console.log('Watch history updated successfully');
        setWatchRecorded(true);
      })
      .catch(err => {
        console.error('Failed to update watch history:', err);
      });
    }, 10000); // 10 seconds
    
    return () => clearTimeout(timer);
  }, [videoId, username, watchStartTime, videoDetails, watchRecorded]);

  // Record completed watch when component unmounts
  useEffect(() => {
    return () => {
      // Only proceed if we have all required data
      if (!videoId || !username || watchStartTime === 0) {
        console.log('Skipping watch history update on unmount due to missing data');
        return;
      }
      
      const watchDuration = Math.floor((Date.now() - watchStartTime) / 1000);
      const videoTitle = videoDetails?.snippet?.title || 'Unknown Video';
      
      // Only record if watched for at least 5 seconds and not already recorded as completed
      if (watchDuration >= 5 && (!watchRecorded || watchDuration > 30)) {
        console.log('Recording completed watch on unmount:', {
          username,
          videoId,
          title: videoTitle,
          watchDuration,
          completed: watchDuration > 30
        });
        
        addToWatchHistory(username, {
          videoId: videoId,
          title: videoTitle,
          watchDuration,
          completed: watchDuration > 30 // Consider completed if watched for more than 30 seconds
        }).catch(err => console.error('Failed to update watch history on unmount:', err));
      }
    };
  }, [videoId, username, watchStartTime, videoDetails, watchRecorded]);

  const handleLike = async () => {
    try {
      await likeVideo(username, videoId as string);
      setLiked(true);
    } catch (err) {
      console.error('Failed to like video:', err);
    }
  };

  const handleBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-4">
        <p className="text-red-500">{error}</p>
        <button 
          onClick={handleBack}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="video-player-container">
      <button 
        onClick={handleBack}
        className="flex items-center text-blue-500 mb-4"
      >
        <ArrowLeft size={16} className="mr-1" /> Back
      </button>
      
      <div className="aspect-video bg-black rounded-lg overflow-hidden">
        {videoId && (
          <iframe
            width="100%"
            height="100%"
            src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`}
            title={videoDetails?.snippet?.title || 'YouTube Video'}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        )}
      </div>
      
      <div className="mt-4">
        <h1 className="text-xl font-bold">{videoDetails?.snippet?.title || 'YouTube Video'}</h1>
        <div className="flex justify-between items-center mt-2">
          <p className="text-sm text-gray-600">{videoDetails?.snippet?.channelTitle || 'YouTube Channel'}</p>
          <div className="flex gap-2">
            <button 
              onClick={handleLike}
              className={`flex items-center gap-1 px-3 py-1 rounded-full ${liked ? 'bg-blue-100 text-blue-600' : 'bg-gray-100'}`}
              disabled={liked}
            >
              <ThumbsUp size={16} /> Like
            </button>
          </div>
        </div>
        <div className="mt-4 bg-gray-50 p-3 rounded-md">
          <p className="text-sm whitespace-pre-line">{videoDetails?.snippet?.description || 'No description available'}</p>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;