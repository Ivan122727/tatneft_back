import os
from moviepy.editor import *


def extract_audio_wav(mp4_file, output_wav):
    video = VideoFileClip(mp4_file)
    video.audio.write_audiofile(output_wav)
    video.close()


def video2audio(mp4=r"", mp3=r"D:\Projects\pythonProject\image_detection\source\output.mp3"):
    FILETOCONVERT = AudioFileClip(mp4)
    FILETOCONVERT.write_audiofile(mp3)
    FILETOCONVERT.close()


if __name__ == "__main__":
    video2audio(r"D:\Projects\pythonProject\image_detection\source\Совещание_короткое.mp4")
    # video2audio()