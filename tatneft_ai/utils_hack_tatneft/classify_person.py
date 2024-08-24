# # -*- coding: utf-8 -*-
# # import torchaudio
# # from speechbrain.pretrained import SpeakerDiarization
# #
# # diarization = SpeakerDiarization.from_hparams(source="speechbrain/spkrec-diarization", savedir="tmpdir")
# #
# # audio_file = "path/to/your/audio/file.wav"
# # signal, fs = torchaudio.load(audio_file)
# #
# # diarization_result = diarization.diarize_file(audio_file)
# # print(diarization_result)
#
# import numpy as np
# import librosa
# from pydub import AudioSegment
# from sklearn.mixture import GaussianMixture
# from typing import List, Dict, Tuple
# import chardet
# import re
# from typing import List, Tuple
#
#
# class SpeakerIdentifier:
#     def __init__(self, n_speakers: int):
#         self.n_speakers = n_speakers
#         self.model = GaussianMixture(n_components=n_speakers, covariance_type='diag')
#
#     def load_audio(self, audio_file: str) -> np.ndarray:
#         audio = AudioSegment.from_mp3(audio_file)
#         audio = audio.set_frame_rate(16000)
#         audio_np = np.array(audio.get_array_of_samples())
#         return audio_np
#
#     def extract_features(self, audio_np: np.ndarray, sr: int) -> np.ndarray:
#         mfccs = librosa.feature.mfcc(y=audio_np, sr=sr, n_mfcc=13)
#         return mfccs
#
#     def train_model(self, features: np.ndarray):
#         self.model.fit(features.T)
#
#     def predict_speakers(self, features: np.ndarray) -> np.ndarray:
#         return self.model.predict(features.T)
#
#     def detect_encoding(self, file_path: str) -> str:
#         with open(file_path, 'rb') as f:
#             raw_data = f.read()
#             result = chardet.detect(raw_data)
#             return result['encoding']
#
#     def parse_transcription_file(self, transcription_file: str) -> List[Tuple[str, float, float]]:
#         transcription = []
#
#         encoding = self.detect_encoding(transcription_file)
#         print(f"Detected encoding: {encoding}")  # Для отладки
#         with open(transcription_file, 'r', encoding=encoding, errors='ignore') as f:
#             file_content = f.read()
#
#         entries = file_content.splitlines()
#
#         for entry in entries:
#             entry = entry.strip()
#             if entry:
#                 match = re.match(r'\[([0-9\.]+)-([0-9\.]+)\] (.+)', entry)
#                 if match:
#                     start_time = float(match.group(1))
#                     end_time = float(match.group(2))
#                     text = match.group(3)
#                     transcription.append((text, start_time, end_time))
#                 else:
#                     print(f"Skipping invalid line: {entry}")
#
#         return transcription
#
#     def match_text_with_audio(self, transcription: List[Tuple[str, float, float]],
#                               audio_segments: List[Dict[str, float]]) -> Dict[str, str]:
#         matches = {}
#         for segment in audio_segments:
#             matched_text = self.find_matching_text(transcription, segment['start_time'], segment['end_time'])
#             matches[f"Segment {segment['start_time']}-{segment['end_time']}"] = matched_text
#         return matches
#
#     def find_matching_text(self, transcription: List[Tuple[str, float, float]], start_time: float,
#                            end_time: float) -> str:
#         for text, start, end in transcription:
#             if start <= start_time <= end and start <= end_time <= end:
#                 return text
#         return ""
#
#     def process_audio(self, audio_file: str, transcription_file: str) -> Dict[str, str]:
#         audio_np = self.load_audio(audio_file)
#         y, sr = librosa.load(audio_file, sr=None)
#         features = self.extract_features(y, sr)
#
#         self.train_model(features)
#
#         speaker_labels = self.predict_speakers(features)
#
#         audio_segments = [{'start_time': i, 'end_time': i + 1} for i in range(len(speaker_labels))]
#
#         transcription = self.parse_transcription_file(transcription_file)
#         return self.match_text_with_audio(transcription, audio_segments)
#
# #
# if __name__ == "__main__":
#     # Путь к вашему аудиофайлу и файлу с транскрипцией
#     audio_file = r"D:\Projects\pythonProject\image_detection\source\output\output.mp3"
#     transcription_file = r"D:\Projects\pythonProject\image_detection\audio2text\result_tiny.txt"
#
#     # Создание экземпляра класса и выполнение обработки
#     speaker_identifier = SpeakerIdentifier(n_speakers=2)
#     results = speaker_identifier.process_audio(audio_file, transcription_file)
#
#     # Печать результатов
#     for segment, text in results.items():
#         print(f"{segment}: {text}")

from pyannote.audio import Pipeline
import whisper

import time

start_time = time.time()
# Загрузка моделей
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.0",
                         use_auth_token="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")

print("step-1")
# pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
whisper_model = whisper.load_model("base")
print("step-2")
audio_file = "D:\Projects\pythonProject\image_detection\source\output\output.mp3"
result = whisper_model.transcribe(audio_file)
print(result["segments"])
input("wait")
print("step-3")
# Диаризация с pyannote.audio
diarization = pipeline(audio_file)
print("step-5")
# Объединение результатов
final_annotations = []
for segment, _, speaker in diarization.itertracks(yield_label=True):
    for i, item in enumerate(result["segments"]):
        if segment.start <= item["start"] < segment.end:
            text = item["text"]
            start = item["start"]
            end = item["end"]
            final_annotations.append(f'(спикер_{speaker})[{start:.2f} - {end:.2f}] {text}')

print(diarization)
print(result)
# Вывод результата
for annotation in final_annotations:
    print(annotation)
end_time = time.time()

print(end_time-start_time)