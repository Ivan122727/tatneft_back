class AudioTextMerger:
    def __init__(self, audio_transcription, face_photos_dict):
        self.audio_transcription = audio_transcription
        self.face_photos_dict = face_photos_dict
        self.speakers = set()

    def update_transcription_with_photos(self):
        updated_transcription = []

        for entry in self.audio_transcription:
            if 'speaker' in entry:
                self.speakers.add(entry['speaker'])

        self.face_photos_dict.sort(key=lambda x: x['time_start'])

        for entry in self.audio_transcription:
            entry_photo = None
            for photo_entry in self.face_photos_dict:
                if photo_entry['time_start'] <= entry['time_end'] and photo_entry['time_end'] >= entry['time_start']:
                    entry_photo = photo_entry['photo']
                    break

            entry['photo'] = entry_photo

            if 'speaker' in entry:
                if entry['speaker'] in self.speakers:
                    entry['role'] = 'participant'
                else:
                    entry['role'] = 'moderator'
            else:
                entry['role'] = 'moderator'

            updated_transcription.append(entry)

        return updated_transcription