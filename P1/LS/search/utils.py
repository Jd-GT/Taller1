# search/utils.py (modificado)
import json
from .abstracts import DataLoader  # Importa la abstracción

class JSONDataLoader(DataLoader):
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)