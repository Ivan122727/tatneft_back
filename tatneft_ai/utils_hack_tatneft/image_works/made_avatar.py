# -*- coding: utf-8 -*-
import cv2
import torch
import torchvision.models as models
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from torchvision.transforms import functional as F
from tqdm import tqdm


def extract_features(image, feature_extractor):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (224, 224))
    image = F.to_tensor(image).unsqueeze(0)
    with torch.no_grad():
        features = feature_extractor(image)
    return features.squeeze().cpu().numpy()


def detect_and_save_unique_persons(video_path, similarity_threshold=0.8):
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.eval()

    feature_extractor = models.resnet18(pretrained=True)
    feature_extractor.fc = torch.nn.Identity()  # Удаляем последний слой
    feature_extractor.eval()

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    unique_persons = []
    person_dict = {}

    intervals = [
        (0, int(total_frames * 0.01), 10),  # Первые 20% кадров - каждый кадр
        (int(total_frames * 0.2), int(total_frames * 0.5), 300),  # Следующие 30% - каждый 5-й кадр
        (int(total_frames * 0.5), total_frames, 700)  # Оставшиеся 50% - каждый 30-й кадр
    ]

    frame_count = 0
    for start, end, step in tqdm(intervals):
        cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        while frame_count < end:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % step == 0:
                results = model(frame)
                for det in results.xyxy[0]:
                    if det[5] == 0:
                        x1, y1, x2, y2 = map(int, det[:4])
                        person = frame[y1:y2, x1:x2]

                        current_features = extract_features(person, feature_extractor)

                        is_unique = True
                        for unique_features in unique_persons:
                            similarity = cosine_similarity([current_features], [unique_features])[0][0]
                            if similarity > similarity_threshold:
                                is_unique = False
                                break

                        if is_unique:
                            unique_persons.append(current_features)
                            person_dict[frame_count] = person

            frame_count += 1
            if frame_count % step != 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
        break

    cap.release()
    return person_dict