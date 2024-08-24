import cv2
import numpy as np
import dlib
from collections import deque
from tqdm import tqdm

import os


class VideoProcessor:
    def __init__(self, input_video_path, output_video_path, frame_skip=60, face_photo_dir='face_photos'):
        self.input_video_path = input_video_path
        self.output_video_path = output_video_path
        self.frame_skip = frame_skip
        self.cap = cv2.VideoCapture(input_video_path)
        self.prev_faces = {}
        self.landmark_histories = {}
        self.face_photos = {}
        self.face_photo_dir = face_photo_dir

        self._folders_cheker()

        folder_sf3_path = r"tatneft_ai/models/shape_predictor/s3fd/"
        folder_shape_predictor_path = r"tatneft_ai/models/shape_predictor"
        LANDMARK_MODEL_PATH = f"{folder_shape_predictor_path}shape_predictor_68_face_landmarks.dat"
        S3FD_MODEL_PATH = f'{folder_sf3_path}SFD.caffemodel'
        S3FD_PROTO_PATH = f'{folder_sf3_path}deploy.prototxt'
        self.ACCUMULATION_FRAMES = 15
        self.SPEECH_THRESHOLD = 0.009

        self.dlib_face_detector = dlib.get_frontal_face_detector()
        self.s3fd_face_detector = cv2.dnn.readNetFromCaffe(S3FD_PROTO_PATH, S3FD_MODEL_PATH)
        self.s3fd_face_detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)  # Use CUDA if available
        self.s3fd_face_detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)  # Use CUDA if available
        self.landmark_predictor = dlib.shape_predictor(LANDMARK_MODEL_PATH)

    def _folders_cheker(self):
        os.makedirs(self.face_photo_dir, exist_ok=True)

        if not self.cap.isOpened():
            raise IOError("Error opening video file.")

    def detect_faces_dlib(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.dlib_face_detector(gray)
        return faces

    def detect_faces_s3fd(self, image):
        height, width = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1.0, (width, height), (104.0, 177.0, 123.0))
        self.s3fd_face_detector.setInput(blob)
        detections = self.s3fd_face_detector.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                (left, top, right, bottom) = box.astype("int")
                faces.append(dlib.rectangle(left, top, right, bottom))

        return faces

    def extract_landmarks(self, image, faces):
        landmarks_list = []
        for face in faces:
            shape = self.landmark_predictor(image, face)
            landmarks = [(point.x, point.y) for point in shape.parts()]
            landmarks_list.append(landmarks)
        return landmarks_list

    def get_face_id(self, face):
        face_center = ((face.left() + face.right()) // 2, (face.top() + face.bottom()) // 2)

        for face_id, (prev_center, _) in self.prev_faces.items():
            if np.linalg.norm(np.array(prev_center) - np.array(face_center)) < 50:
                return face_id
        new_face_id = max(self.prev_faces.keys() or [0]) + 1
        return new_face_id

    def normalize_landmarks(self, landmarks, face_height):
        mouth_top = landmarks[51]
        mouth_bottom = landmarks[57]
        mouth_center = ((mouth_top[0] + mouth_bottom[0]) // 2, (mouth_top[1] + mouth_bottom[1]) // 2)

        normalized = []
        for lm in landmarks:
            normalized.append(((lm[0] - mouth_center[0]) / face_height, (lm[1] - mouth_center[1]) / face_height))

        return normalized

    def detect_speech(self, landmark_history):
        # get idea from paper https://arxiv.org/pdf/2110.13806
        if len(landmark_history) < self.ACCUMULATION_FRAMES:
            return False

        upper_lip = [frame[51][1] for frame in landmark_history]
        lower_lip = [frame[57][1] for frame in landmark_history]
        left_corner = [frame[48][0] for frame in landmark_history]
        right_corner = [frame[54][0] for frame in landmark_history]

        t = np.array(upper_lip)
        b = np.array(lower_lip)
        l = np.array(left_corner)
        r = np.array(right_corner)

        t_smooth = np.convolve(t, np.ones(3) / 3, mode='same')
        b_smooth = np.convolve(b, np.ones(3) / 3, mode='same')
        l_smooth = np.convolve(l, np.ones(3) / 3, mode='same')
        r_smooth = np.convolve(r, np.ones(3) / 3, mode='same')

        d = np.abs(t - t_smooth)
        e = np.abs(b - b_smooth)
        f = np.abs(l - l_smooth)
        g = np.abs(r - r_smooth)

        c = (d + e + f + g) / 4

        movement = np.mean(c)
        max_movement = np.max(c)

        return movement > self.SPEECH_THRESHOLD

    def save_face_photo(self, frame, face, face_id):
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        face_image = frame[y:y+h, x:x+w]

        if face_image.size == 0:
            print(f"Warning: Face image for ID {face_id} is empty. Skipping save.")
            return None

        photo_path = os.path.join(self.face_photo_dir, f'face_{face_id}.jpg')
        if not cv2.imwrite(photo_path, face_image):
            print(f"Error: Could not write face photo for ID {face_id} to {photo_path}.")
            return None

        return photo_path

    def process_video(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_fps = self.cap.get(cv2.CAP_PROP_FPS)
        output_size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                       int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        out = cv2.VideoWriter(self.output_video_path, fourcc, output_fps, output_size)

        communications = []
        face_photos = {}

        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        halfway_point = total_frames // 2

        current_frame = 0
        use_s3fd = False
        speaking_faces = {}

        # Create a tqdm progress bar
        with tqdm(total=halfway_point, desc='Processing Video', unit='frame') as pbar:
            while True:
                ret, frame = self.cap.read()
                if not ret or current_frame >= halfway_point or current_frame > 300:
                    break

                if current_frame % 2 == 0:
                    current_frame += 1
                    continue

                if current_frame % self.frame_skip == 0:
                    use_s3fd = True
                else:
                    use_s3fd = False

                if use_s3fd:
                    faces = self.detect_faces_s3fd(frame)
                else:
                    faces = self.detect_faces_dlib(frame)

                landmarks = self.extract_landmarks(frame, faces)

                current_faces = {}
                for face, lmks in zip(faces, landmarks):
                    face_id = self.get_face_id(face)
                    face_center = ((face.left() + face.right()) // 2, (face.top() + face.bottom()) // 2)
                    current_faces[face_id] = (face_center, lmks)

                    face_height = face.height()
                    normalized_lmks = self.normalize_landmarks(lmks, face_height)

                    if face_id not in self.landmark_histories:
                        self.landmark_histories[face_id] = deque(maxlen=self.ACCUMULATION_FRAMES)
                    self.landmark_histories[face_id].append(normalized_lmks)

                    speaking = self.detect_speech(self.landmark_histories[face_id])

                    if speaking:
                        if face_id not in speaking_faces:
                            speaking_faces[face_id] = {
                                'start_time': current_frame / output_fps,
                                'photo': self.save_face_photo(frame, face, face_id)
                            }
                    else:
                        if face_id in speaking_faces:
                            speaking_faces[face_id]['end_time'] = current_frame / output_fps
                            face_photos[face_id] = speaking_faces[face_id]['photo']
                            speaking_faces.pop(face_id)

                    if os.environ.get("DRAW_MASK", None) is not None:
                        cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)

                        for (x, y) in lmks:
                            cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

                        color = (0, 255, 0) if speaking else (0, 0, 255)
                        cv2.circle(frame, face_center, 10, color, -1)

                        status_text = "Speaking" if speaking else "Not Speaking"
                        cv2.putText(frame, f'Person {face_id}: {status_text}', (face.left(), face.top() - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

                    if face_id not in face_photos:
                        face_photos[face_id] = self.save_face_photo(frame, face, face_id)

                self.landmark_histories = {k: v for k, v in self.landmark_histories.items() if k in current_faces}
                self.prev_faces = current_faces

                out.write(frame)
                current_frame += 1

                pbar.update(1)

        for face_id in speaking_faces:
            speaking_faces[face_id]['end_time'] = current_frame / output_fps
            face_photos[face_id] = speaking_faces[face_id]['photo']

        self.cap.release()
        out.release()

        face_photos_dict = [
            {"time_start": info['start_time'], "time_end": info.get('end_time', current_frame / output_fps),
             "speaker": f'Person {face_id}', "photo": info['photo']}
            for face_id, info in speaking_faces.items()
        ]

        return face_photos_dict
