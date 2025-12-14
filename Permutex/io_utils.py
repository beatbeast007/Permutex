"""
IO Utilities for Permutex
Provides safe file writing methods.
"""

import os

def safe_write_text(path: str, text: str, mode: str = 'w') -> None:
    """
    Safely writes text to a file, creating parent directories if needed.

    Args:
        path (str): Destination file path.
        text (str): Text content to write.
        mode (str): File mode ('w' for overwrite, 'a' for append). Default is 'w'.
    """
    try:
        directory = os.path.dirname(path) or '.'
        os.makedirs(directory, exist_ok=True)

        with open(path, mode, encoding='utf-8', errors='ignore') as f:
            f.write(text)
    except Exception as e:
        raise IOError(f"Failed to write to file: {path}") from e
