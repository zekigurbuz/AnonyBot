import os
import json

from config import *

class Setting(object):
    def __init__(self, value=None):
        self.value = value

    def is_none(self):
        return self.value is None

    def get(self):
        answer = self.get_or_default(None)
        if answer is None:
            raise ValueError("Attempting to get a None")

        return answer

    def get_or_default(self, defualt):
        if self.value:
            return self.value
        else:
            return value

class Data(object):
    def __init__(self, data):
        self.data = data
        if not os.path.exists(data):
            os.mkdir(data)

    def save(self, key, value):
        path = os.path.join(self.data, key)
        with open(path, "w", encoding="UTF-8") as cache:
            json.dump(value, cache)

    def load(self, key) -> Setting:
        path = os.path.join(data, key)
        if not os.path.exists(path):
            return Setting(None)
        with open(path, "r", encoding="UTF-8") as cache:
            return Setting(json.load(cache))
