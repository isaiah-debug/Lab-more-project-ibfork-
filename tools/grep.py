"""
The grep tool searches matching project files for lines that match a regex.
"""

import glob
import re
from chat import is_path_safe


def run_grep(pattern, path_glob):
    """
    Search matching files for lines that match a regex.

    >>> import os, tempfile
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     f1 = os.path.join(tmp, "a.txt")
    ...     f2 = os.path.join(tmp, "b.txt")
    ...     _ = open(f1, "w", encoding="utf-8").write("hello world\\nfoo")
    ...     _ = open(f2, "w", encoding="utf-8").write("bar\\nhello again")
    ...     run_grep("hello", os.path.join(tmp, "*.txt"))
    'hello world\\nhello again'

    >>> run_grep("hello", "..")
    'Error: unsafe path'

    >>> import os, tempfile
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     f = os.path.join(tmp, "a.txt")
    ...     _ = open(f, "w", encoding="utf-8").write("nothing here")
    ...     run_grep("xyz", os.path.join(tmp, "*.txt"))
    ''
    """
    if not is_path_safe(path_glob):
        return "Error: unsafe path"

    out = []
    for filename in sorted(glob.glob(path_glob)):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    if re.search(pattern, line):
                        out.append(line.rstrip("\n"))
        except Exception:
            continue

    return "\n".join(out)
