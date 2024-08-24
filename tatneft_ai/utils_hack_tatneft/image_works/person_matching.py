# -*- coding: utf-8 -*-
import cv2
import numpy as np
import librosa
from moviepy.editor import VideoFileClip


# Function to detect faces using OpenCV
def detect_faces(frame, face_cascade):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces


# Function to extract audio features using librosa
def extract_audio_features(audio_path, start_time, end_time):
    y, sr = librosa.load(audio_path, offset=start_time, duration=end_time - start_time)
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    return mfcc


# Main function to match speakers to photos
def match_speakers_to_photos(video_path, audio_path, replics):
    # Load the video and audio
    # video = VideoFileClip(video_path)
    # audio, sr = librosa.load(audio_path)

    # Initialize the face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print("cascade builded")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    speaker_photos = {}

    print("infinite loop")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        faces = detect_faces(frame, face_cascade)
        time = frame_count / fps
        matching_replic = next((r for r in replics if r["start"] <= time < r["end"]), None)

        if matching_replic and len(faces) > 0:
            speaker = matching_replic["speaker"]
            if speaker not in speaker_photos:
                x, y, w, h = faces[0]  # Coordinates of the first face
                face_image = frame[y:y + h, x:x + w]
                speaker_photos[speaker] = face_image

        frame_count += 1
    cap.release()
    return speaker_photos


if __name__ == "__main__":
    # Пример использования
    video_path = r"D:\Projects\pythonProject\image_detection\source\video.mp4"
    audio_path = r"D:\Projects\pythonProject\image_detection\source\output\example.mp3"
    replics = [
        {"speaker": "Speaker 1", "start": 0.0, "end": 5.0, "text": "Hello"},
        {"speaker": "Speaker 2", "start": 5.0, "end": 10.0, "text": "Hi there"},
        # ... добавьте остальные реплики
    ]

    speaker_photos = match_speakers_to_photos(video_path, audio_path, replics)
    print(speaker_photos)