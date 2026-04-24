"""
The cat tool reads a text file in the current project and returns its contents.
"""

import platform

from chat import is_path_safe


TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "cat",
        "description": "Read a text file from the current project and return its contents.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The relative path of the text file to read.",
                }
            },
            "required": ["path"],
        },
    },
}


def read_text_file(path):
    """
    Read a text file with the encodings supported by the current platform.

    >>> import os, shutil
    >>> test_dir = "__doctest_read_text_tmp__"
    >>> shutil.rmtree(test_dir, ignore_errors=True)
    >>> os.makedirs(test_dir)
    >>> file_path = os.path.join(test_dir, "sample.txt")
    >>> _ = open(file_path, "w", encoding="utf-8").write("alpha")
    >>> read_text_file(file_path)
    'alpha'
    >>> shutil.rmtree(test_dir)
    """
    encodings = ["utf-8"]
    if platform.system() == "Windows":
        encodings.append("utf-16")

    last_error = None
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as file_handle:
                return file_handle.read()
        except UnicodeDecodeError as error:
            last_error = error

    if last_error is not None:
        raise last_error


def run_cat(path):
    """
    Read and return the contents of a text file.

    >>> import os, shutil
    >>> test_dir = "__doctest_cat_tmp__"
    >>> shutil.rmtree(test_dir, ignore_errors=True)
    >>> os.makedirs(test_dir)
    >>> path = os.path.join(test_dir, "hello.txt")
    >>> _ = open(path, "w", encoding="utf-8").write("hello\\nworld")
    >>> run_cat(path)
    'hello\\nworld'
    >>> shutil.rmtree(test_dir)

    >>> run_cat("..")
    'Error: unsafe path'

    >>> run_cat("definitely_not_a_real_file_123.txt").startswith("Error:")
    True
    """
    if not is_path_safe(path):
        return "Error: unsafe path"

    try:
        return read_text_file(path)
    except Exception as error:
        return f"Error: {error}"
