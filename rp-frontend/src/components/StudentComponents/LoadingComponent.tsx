import {
  BeatLoader,
  ClimbingBoxLoader,
  DotLoader,
  HashLoader,
  PacmanLoader,
} from "react-spinners";
import { useEffect, useState } from "react";
import React from "react";

const loaders = [
  { component: BeatLoader, color: "#6366F1", size: 35 },
  { component: ClimbingBoxLoader, color: "#EC4899", size: 25 },
  { component: DotLoader, color: "#10B981", size: 100 },
  { component: HashLoader, color: "#8B5CF6", size: 80 },
  { component: PacmanLoader, color: "#F59E0B", size: 50 },
];

const LoadingComponent = ({ isLoading }: { isLoading: boolean }) => {
  const [loaderIndex, setLoaderIndex] = useState(0);

  useEffect(() => {
    if (!isLoading) return;

    const interval = setInterval(() => {
      setLoaderIndex((prevIndex) => (prevIndex + 1) % loaders.length);
    }, 5000); // switch loader every 5s

    return () => clearInterval(interval);
  }, [isLoading]);

  const { component: LoaderComponent, color, size } = loaders[loaderIndex];

  return (
    <>
      {isLoading && (
        <div className="mt-6 flex flex-col items-center space-y-6">
          <div className="h-40 flex items-center justify-center">
            <LoaderComponent color={color} size={size} />
          </div>{" "}
          <p className="text-5xl font-semibold text-blue-500 animate-bounce text-center">
            Sending your recording...
          </p>
          <p className="text-md font-medium text-purple-400 animate-pulse text-center">
            Please wait, we are processing your audio!
          </p>
        </div>
      )}
    </>
  );
};

export default LoadingComponent;
