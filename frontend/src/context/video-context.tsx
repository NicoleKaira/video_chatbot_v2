"use client"

import {createContext, useContext, ReactNode, useState, useEffect} from 'react';

interface VideoContextProps {
  videoId: string,
  videoName: string;
  summary: string;
  setVideoData: (videoId: string, videoName: string, summary: string) => void;
}

const VideoContext = createContext<VideoContextProps | undefined>(undefined);

export const VideoProvider = ({ children }: { children: ReactNode }) => {
  const storedVideoId = typeof window !== "undefined" ? localStorage.getItem('videoId') : null;
  const storedVideoName = typeof window !== "undefined" ? localStorage.getItem('videoName') : null;
  const storedSummary = typeof window !== "undefined" ? localStorage.getItem('summary') : null;

  const [videoId, setVideoId] = useState<string>(storedVideoId || '');
  const [videoName, setVideoName] = useState<string>(storedVideoName || '');
  const [summary, setSummary] = useState<string>(storedSummary || '');

  const setVideoData = (videoId: string, videoName: string, summary: string) => {
    setVideoName(videoName);
    setSummary(summary);
    setVideoId(videoId);

    if (typeof window !== "undefined") {
      localStorage.setItem('videoId', videoId);
      localStorage.setItem('videoName', videoName);
      localStorage.setItem('summary', summary);
    }
  };

  useEffect(() => {
    if (videoId && videoName && summary) {
      setVideoData(videoId, videoName, summary);
    }
  }, [videoId, videoName, summary]);

  return (
    <VideoContext.Provider value={{ videoId, videoName, summary, setVideoData }}>
      {children}
    </VideoContext.Provider>
  );
};

export const useVideoContext = () => {
  const context = useContext(VideoContext);
  if (!context) {
    throw new Error('useVideoContext must be used within a VideoProvider');
  }
  return context;
};
