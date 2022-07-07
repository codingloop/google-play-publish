import json
from json import JSONDecodeError
from typing import Any


def read_config(file_path: str) -> Any[dict, list]:
    try:
        with open(file_path) as f:
            data = json.load(f)

        return data

    except FileNotFoundError:
        raise Exception(f"No file found in the path {file_path}\n"
                        f"No such file or directory: {file_path}")

    except JSONDecodeError as e:
        raise Exception(f"Error reading JSON file. Please provide valid JSON file\n{e.args}")

