# """
# YouTube Video Downloader and High-Resolution Merger
# 
# This script downloads YouTube videos in high resolution by:
# 1. Downloading the best video-only stream (without audio)
# 2. Downloading the best audio-only stream
# 3. Merging them using FFmpeg for optimal quality
# 
# Requirements:
# - pytubefix: pip install pytubefix
# - FFmpeg: Must be installed and added to system PATH
#   - Windows: Download from https://ffmpeg.org/download.html
#   - Mac: brew install ffmpeg
#   
# 
# Usage:
# 1. Replace the 'url' variable with your YouTube video URL
# 2. Run: python download.py
# 3. The merged video will be saved as 'highres_output.mp4'
# 
# Note: This approach separates video and audio streams to achieve higher quality
# than downloading a single combined stream, especially for high-resolution videos.
# 
# Source: Based on FFmpeg guide from https://youtu.be/DMEP82yrs5g?si=bfjFkgl9x_qHUd6h
# """

# =============================================================================
# NEW APPROACH - Using yt-dlp (RECOMMENDED)
# =============================================================================
"""
YouTube Video Downloader using yt-dlp

This script uses yt-dlp (a fork of youtube-dl) to download YouTube videos
in the highest available quality. yt-dlp automatically handles:
- Best video and audio stream selection
- Automatic merging with FFmpeg
- Resume capability for interrupted downloads
- Better error handling and retry logic

Requirements:
- yt-dlp: pip install yt-dlp
- FFmpeg: Must be installed and added to system PATH
  - Windows: Download from https://ffmpeg.org/download.html
  - Mac: brew install ffmpeg
  - Linux: sudo apt install ffmpeg

Usage:
1. Replace the 'url' variable with your YouTube video URL
2. Run: python download.py
3. Video will be saved as '[video_title].mp4'

"""

import yt_dlp

# YouTube video URLs to download
# url = 'https://www.youtube.com/live/gn-GUwOsLMo?si=sWr43jlFXXVKcSlZ'  # Dr. Loke Lecture 1
# url = 'https://www.youtube.com/live/Z_T09vQpl00?si=QyCTA2BGhEl2ZZaE'  # Dr. Loke Lecture 2
# url = 'https://www.youtube.com/live/xyuTU3v_qWs?si=b0s2yJdmxXiSDxq8' #Dr.loke Lecture 3
# url = 'https://www.youtube.com/live/X3xCckK_qfk?si=l9n952oSZC1SJcj9' #Dr Loke Lecture 4
url ='https://www.youtube.com/live/PkZn5gipMRE?si=7Sktmi5cxRPSFyh8' #Dr Loke Lecture 5

# Configuration options for yt-dlp
ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',      # Save as video_title.mp4
    'format': 'bestvideo+bestaudio/best', # Get best video+audio, fallback to best combined
    'merge_output_format': 'mp4',         # Merge using ffmpeg to MP4 format
    'noplaylist': True,                   # Don't download playlists, just the video
    'retries': 10,                        # Retry failed downloads up to 10 times
    'fragment_retries': 10,               # Retry failed fragments up to 10 times
    'continuedl': True,                   # Resume interrupted downloads
    'verbose': True                       # Show detailed progress information
}

# Download the video using yt-dlp
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("\n Download completed! Check the current directory for the video file.")



# =============================================================================
# OLD APPROACH (COMMENTED OUT) - Using pytubefix
# =============================================================================
# This section shows the previous method using pytubefix library
# It manually separates video and audio streams, then merges with FFmpeg
# 
# from pytubefix import YouTube
# from pytubefix.cli import on_progress
# import os
# 
# # YouTube video URL to download
# url = "https://www.youtube.com/live/Z_T09vQpl00?si=QyCTA2BGhEl2ZZaE"
# yt = YouTube(url, on_progress_callback=on_progress)
# 
# print("Title:", yt.title)
# 
# # Download best high-resolution video-only stream
# video_stream = yt.streams.filter(adaptive=True, only_video=True, file_extension='mp4').order_by('resolution').desc().first()
# video_path = video_stream.download(filename='temp_video.mp4')
# print("Video downloaded:", video_path)
# 
# # Download best audio-only stream
# audio_stream = yt.streams.filter(adaptive=True, only_audio=True, file_extension='mp4').order_by('abr').desc().first()
# audio_path = audio_stream.download(filename='temp_audio.mp4')
# print("Audio downloaded:", audio_path)
# 
# # Merge using FFmpeg (requires ffmpeg installed and added to PATH)
# output_path = "highres_output.mp4"
# os.system(f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -strict experimental "{output_path}"')
# 
# print("\n Done! High-resolution video saved as:", output_path)
# 
# # Clean up temporary files (optional)
# # os.remove(video_path)
# # os.remove(audio_path)

