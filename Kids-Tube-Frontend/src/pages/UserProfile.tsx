import React, { useState, useEffect } from 'react';
import { getWatchHistory, getUserDebug } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Clock, ThumbsUp, Bug } from 'lucide-react';
import { useUser } from '../context/UserContext';

const UserProfile: React.FC = () => {
  const { username } = useUser();
  const [watchHistory, setWatchHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<any>(null);
  const [showDebug, setShowDebug] = useState<boolean>(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchWatchHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('Fetching watch history for:', username);
        const history = await getWatchHistory(username);
        console.log('Fetched watch history:', history);
        
        if (Array.isArray(history)) {
          setWatchHistory(history);
        } else {
          console.error('Invalid watch history format:', history);
          setError('Invalid watch history data format');
          setWatchHistory([]);
        }
      } catch (err) {
        console.error('Failed to load watch history:', err);
        setError('Failed to load watch history. Please try again later.');
        setWatchHistory([]);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchWatchHistory();
    }
  }, [username]);

  const handleVideoClick = (videoId: string) => {
    navigate(`/video/${videoId}`);
  };

  const handleDebugClick = async () => {
    try {
      const debug = await getUserDebug(username);
      console.log('User debug info:', debug);
      setDebugInfo(debug);
      setShowDebug(true);
    } catch (err) {
      console.error('Failed to get debug info:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold mb-2">Hi, {username}!</h1>
            <p className="text-gray-600">Here's your activity on Kids YouTube</p>
          </div>
          <button
            onClick={handleDebugClick}
            className="flex items-center text-gray-500 hover:text-blue-600"
          >
            <Bug size={18} className="mr-1" /> Debug
          </button>
        </div>
      </div>

      {showDebug && debugInfo && (
        <div className="bg-gray-100 rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Bug size={20} className="mr-2" /> Debug Information
          </h2>
          <pre className="bg-gray-800 text-green-400 p-4 rounded-md overflow-x-auto text-sm">
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
          <button
            onClick={() => setShowDebug(false)}
            className="mt-4 px-4 py-2 bg-gray-500 text-white rounded-md"
          >
            Hide Debug Info
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center">
          <Clock size={20} className="mr-2" /> Watch History
        </h2>

        {watchHistory.length === 0 ? (
          <div>
            <p className="text-gray-500">You haven't watched any videos yet.</p>
            <p className="text-sm text-gray-400 mt-2">
              Try watching some videos to see them appear here.
            </p>
            <button
              onClick={() => navigate('/')}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md"
            >
              Find Videos to Watch
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {watchHistory.map((item, index) => (
              <div 
                key={index} 
                className="flex items-start p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
                onClick={() => handleVideoClick(item.videoId)}
              >
                <div className="flex-1">
                  <h3 className="font-medium">{item.title}</h3>
                  <p className="text-sm text-gray-500">
                    Watched {new Date(item.watchedAt).toLocaleDateString()}
                  </p>
                  {item.completed && (
                    <span className="inline-flex items-center text-xs text-green-600 mt-1">
                      <ThumbsUp size={12} className="mr-1" /> Completed
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile;