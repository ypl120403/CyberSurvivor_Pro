# core/save_manager.py
import json
import os

class SaveManager:
    def __init__(self):
        self.path = "data/save.json"
        self.data = {
            "currency": 0,
            "unlocked_characters": ["cypher_ghost"],
            "meta_upgrades": {"hp": 0, "atk": 0, "speed": 0},
            "achievements": []
        }
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.data.update(json.load(f))

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

save_manager = SaveManager()