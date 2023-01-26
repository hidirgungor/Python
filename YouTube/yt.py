import urllib.request
import subprocess

# YouTube video URL
url = "https://www.youtube.com/watch?v=wgsWR2dpPyg"

# Download the video file
urllib.request.urlretrieve(url, "video.mp4")

# Use FFmpeg to convert the video to an MP3 file
subprocess.call(["ffmpeg", "-i", "video.mp4", "audio.mp3"])
