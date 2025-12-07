import csv

class FileSingleton:
    _instance = None

    def __init__(self):
        if FileSingleton._instance is not None:
            raise Exception("This class is a singleton!")
        FileSingleton._instance = self

    @staticmethod
    def get_instance():
        if FileSingleton._instance is None:
            FileSingleton()
        return FileSingleton._instance

    def read_csv(self, path):
        try:
            with open(path, newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            return []
        except Exception as e:
            raise Exception(f"Error reading CSV file {path}: {str(e)}")