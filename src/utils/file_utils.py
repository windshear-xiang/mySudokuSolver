import json_tricks as json

def save_sudoku(obj, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(obj, file, indent=None)

def load_sudoku(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        ret = json.load(file)
    return ret