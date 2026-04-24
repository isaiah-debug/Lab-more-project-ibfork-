"""
The ls tool lists files in the current directory or in a specified relative directory.
"""

import glob
import os

from chat import is_path_safe


TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "ls",
        "description": "List files in the current folder or in a specified relative folder.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "An optional relative folder to inspect.",
                }
            },
        },
    },
}


def run_ls(path="."):
    """
    List files in the current folder or a specified relative folder.

    >>> import shutil
    >>> test_dir = "__doctest_ls_tmp__"
    >>> shutil.rmtree(test_dir, ignore_errors=True)
    >>> os.makedirs(test_dir)
    >>> open(os.path.join(test_dir, "b.txt"), "w", encoding="utf-8").close()
    >>> open(os.path.join(test_dir, "a.txt"), "w", encoding="utf-8").close()
    >>> run_ls(test_dir)
    'a.txt\\nb.txt'
    >>> shutil.rmtree(test_dir)

    >>> run_ls("..")
    'Error: unsafe path'
    """
    if not is_path_safe(path):
        return "Error: unsafe path"

    pattern = os.path.join(path, "*") if path != "." else "*"
    matches = sorted(glob.glob(pattern))
    cleaned = [os.path.basename(match.rstrip(os.sep)) for match in matches]
    return "\n".join(cleaned)
