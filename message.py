import json

class message:
    def __init__(self):
        self.dict = {}

    @classmethod
    def from_json(cls, text):
        try:
            self.dict = json.load(text)
        except ValueError:
            print("not a valid json message")
