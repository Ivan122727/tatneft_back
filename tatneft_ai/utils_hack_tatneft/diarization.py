import os

import torch
from pyannote.audio import Pipeline
import pickle


class PersonAssociator:
    def __init__(self):
        self.auth_token = os.environ.get("AUTH_TOKEN_DIARIZATION", "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")
        self.path_save_ai_model = os.environ.get("source/models/pyannote.pkl", "default_model_path")
        self.pipeline = None

    def load_pipeline(self):
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"Choosen device: {device}")
            self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.0",
                                                     use_auth_token=self.auth_token).to(device)
        except Exception as e:
            print(f"Not downloaded from internet: {e}")
            try:
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                print(f"Choosen device: {device}")
                self.pipeline = Pipeline.from_pretrained(self.path_save_ai_model).to(device)
            except Exception as e:
                print(f"Not uses local versions: {e}")
                raise

    def associate_persons(self, audio_file, save_pickle=False):
        if not self.pipeline:
            print("upload")
            self.load_pipeline()

        diarization = self.pipeline(audio_file)

        if save_pickle:
            self.save_diarization(diarization, audio_file)

        return diarization

    def process_audio(self, audio_file, use_cached=False):
        if use_cached:
            diarization = self.load_diarization(audio_file)
            if diarization:
                return diarization

        return self.associate_persons(audio_file)

    def load_diarization(self, audio_file):
        pickle_file = f"{os.path.splitext(audio_file)[0]}_diarization.pkl"
        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as f:
                return pickle.load(f)
        else:
            print(f"Pickle file not found: {pickle_file}")
            return None

    def save_diarization(self, diarization, audio_file):
        pickle_file = f"{os.path.splitext(audio_file)[0]}_diarization.pkl"
        with open(pickle_file, 'wb') as f:
            pickle.dump(diarization, f)
        print(f"Diarization saved to {pickle_file}")