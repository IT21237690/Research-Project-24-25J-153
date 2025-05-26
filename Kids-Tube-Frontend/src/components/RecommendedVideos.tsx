import React, { useEffect, useState } from 'react';
import { getRecommendations } from '../services/api';
import VideoCard from './VideoCard';
import { RefreshCw } from 'lucide-react';

interface RecommendedVideosProps {
  username: string;
  excludeVideoId?: string;
  onVideoSelect?: (videoId: string) => void;
}

const RecommendedVideos: React.FC<RecommendedVideosProps> = ({ 
  username, 
  excludeVideoId,
  onVideoSelect
}) => {
  const [videos, setVideos] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching recommendations for:', username);
      const recommendedVideos = await getRecommendations(username, 10);
      console.log('Received recommendations:', recommendedVideos);
      
      // Filter out the current video if excludeVideoId is provided
      const filteredVideos = excludeVideoId 
        ? recommendedVideos.filter((video: any) => {
            const videoId = video.videoId || (video.id && (typeof video.id === 'string' ? video.id : video.id.videoId));
            return videoId !== excludeVideoId;
          })
        : recommendedVideos;
      
      setVideos(filteredVideos);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (username) {
      fetchRecommendations();
    }
  }, [username, excludeVideoId]);

  const handleRefresh = () => {
    fetchRecommendations();
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {[...Array(6)].map((_, index) => (
          <div key={index} className="bg-gray-200 animate-pulse h-48 rounded-lg"></div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-4">
        <p className="text-red-500 mb-4">{error}</p>
        <button
          onClick={handleRefresh}
          className="flex items-center mx-auto px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          <RefreshCw size={16} className="mr-2" /> Try Again
        </button>
      </div>
    );
  }

  if (!videos || videos.length === 0) {
    return (
      <div className="text-center p-4">
        <p className="text-gray-500">No recommendations available yet. Watch more videos!</p>
        <p className="text-sm text-gray-400 mt-2">Try searching for some videos to get started.</p>
        <button
          onClick={handleRefresh}
          className="mt-4 flex items-center mx-auto px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          <RefreshCw size={16} className="mr-2" /> Refresh
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div></div> {/* Empty div for spacing */}
        <button
          onClick={handleRefresh}
          className="flex items-center text-blue-500 hover:text-blue-700"
        >
          <RefreshCw size={16} className="mr-1" /> Refresh
        </button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {videos.map((video, index) => (
          <VideoCard 
            key={index} 
            video={video}
            onVideoSelect={onVideoSelect}
          />
        ))}
      </div>
    </div>
  );
};

export default RecommendedVideos;