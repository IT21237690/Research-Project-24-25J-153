import React from "react";
import { useParams } from "react-router-dom";
import VideoPlayer from "../components/VideoPlayer";
import RecommendedVideos from "../components/RecommendedVideos";
import { useUser } from "../context/UserContext";

const VideoPage: React.FC = () => {
  const { videoId } = useParams<{ videoId: string }>();
  const { username } = useUser();

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <VideoPlayer username={username} />
        </div>
        <div>
          <h2 className="text-xl font-bold mb-4">Recommended Videos</h2>
          <RecommendedVideos username={username} excludeVideoId={videoId} />
        </div>
      </div>
    </div>
  );
};

export default VideoPage;