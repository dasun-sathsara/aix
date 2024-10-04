import os
from pathlib import Path


def read_system_prompt(name: str, directory: str = 'system_prompts') -> str:
    """
    Reads the content of a specific system prompt file from a specified directory.
    """

    for file in os.listdir(directory):
        file_name = Path(file).stem
        if file_name == name:
            with (Path(directory) / file).open() as f:
                return f.read().strip()

    raise FileNotFoundError(f"System prompt file '{name}' not found in '{directory}'")
