from pytube import YouTube
from moviepy.editor import *
import os

def convert_to_mp3(video_url):
    try:
        # Youtube videosunu çeker
        yt = YouTube(video_url)

        # Videoyu en yüksek kalitede indirir
        video = yt.streams.get_highest_resolution()
        video.download()

        # İndirilen video dosyasının yolunu ayarlar
        video_path = video.default_filename
        print(f"Video indirildi: {video_path}")

        # Sesi ayıklar ve MP3 olarak kaydeder
        mp4_file = video_path
        mp3_file = video_path[:-4] + '.mp3'
        video_clip = VideoFileClip(mp4_file)
        video_clip.audio.write_audiofile(mp3_file)

        video_clip.close()
        os.remove(mp4_file)

        print(f"MP3 dosyası '{mp3_file}' başarıyla oluşturuldu!")

    except Exception as e:
        print(f"Hata: {str(e)}")

# Örnek kullanım
video_url = input("Youtube video URL'si girin: ")
convert_to_mp3(video_url)