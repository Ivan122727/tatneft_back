from copy import deepcopy


class Person:
    def __init__(self, id=1):
        self.id = id
        self.replics = []
        self.avatars = []

    def add_replic(self, replica): # replica should be {"time_start": int, "time_end": int, "text": text}
        self.replics.append(
            replica
        )

    def add_avatar(self, frame):
        self.avatars = deepcopy(frame)

    def get_json(self):
        return {
            "id": self.id,
            "replics": self.replics,
            "avatars": self.avatars,
        }