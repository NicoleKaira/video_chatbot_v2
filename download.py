from pytubefix import YouTube
from pytubefix.cli import on_progress
import os

url = "https://www.youtube.com/live/gn-GUwOsLMo?si=AZTM6pTcRL4HTmz0"
yt = YouTube(url, on_progress_callback=on_progress)

print("Title:", yt.title)

# Download best video
video_stream = yt.streams.filter(adaptive=True, only_video=True, file_extension='mp4').order_by('resolution').desc().first()
video_path = video_stream.download(filename='video.mp4')

# Download best audio
audio_stream = yt.streams.filter(adaptive=True, only_audio=True, file_extension='mp4').order_by('abr').desc().first()
audio_path = audio_stream.download(filename='audio.mp4')

# Merge using FFmpeg
output_path = 'merged_output.mp4'
os.system(f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -strict experimental "{output_path}"')

print("\nDone: Merged into", output_path)