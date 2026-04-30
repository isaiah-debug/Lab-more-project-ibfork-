"""Unit tests for tool modules and their safety behavior."""

import json
from unittest.mock import patch

from chat import Chat
from tools.calculate import TOOL_SPEC as CALCULATE_TOOL_SPEC
from tools.calculate import run_calculate
from tools.cat import TOOL_SPEC as CAT_TOOL_SPEC
from tools.cat import read_text_file, run_cat
from tools.compact import TOOL_SPEC as COMPACT_TOOL_SPEC
from tools.compact import run_compact
from tools.grep import TOOL_SPEC as GREP_TOOL_SPEC
from tools.grep import run_grep
from tools.ls import TOOL_SPEC as LS_TOOL_SPEC
from tools.ls import run_ls


def test_tool_specs_have_expected_names():
    """Expose the expected tool names to the automatic tool caller."""
    assert LS_TOOL_SPEC["function"]["name"] == "ls"
    assert CAT_TOOL_SPEC["function"]["name"] == "cat"
    assert GREP_TOOL_SPEC["function"]["name"] == "grep"
    assert CALCULATE_TOOL_SPEC["function"]["name"] == "calculate"
    assert COMPACT_TOOL_SPEC["function"]["name"] == "compact"


def test_ls_unsafe():
    """Reject unsafe ls paths."""
    assert run_ls("..") == "Error: unsafe path"


def test_ls_normal():
    """Return a string listing for normal ls calls."""
    result = run_ls(".")
    assert "chat.py" in result.splitlines()


def test_cat_unsafe():
    """Reject unsafe cat paths."""
    assert run_cat("..") == "Error: unsafe path"


def test_read_text_file():
    """Read plain UTF-8 text files."""
    assert "Main entry point" in read_text_file("chat.py")


def test_read_text_file_windows_utf16(tmp_path):
    """Fall back to UTF-16 decoding on Windows."""
    file_path = tmp_path / "utf16.txt"
    file_path.write_text("hello", encoding="utf-16")
    with patch("platform.system", return_value="Windows"):
        assert read_text_file(str(file_path)) == "hello"


def test_read_text_file_decode_error():
    """Raise the final decode error when all supported encodings fail."""
    decode_error = UnicodeDecodeError(
        "utf-8",
        b"\xff",
        0,
        1,
        "invalid start byte",
    )
    with patch("platform.system", return_value="Windows"):
        with patch("builtins.open", side_effect=[decode_error, decode_error]):
            try:
                read_text_file("bad.txt")
            except UnicodeDecodeError as error:
                assert error is decode_error
            else:
                raise AssertionError("Expected UnicodeDecodeError")


def test_cat_missing_file():
    """Return an error for missing files."""
    assert "Error:" in run_cat("not_a_real_file_123.txt")


def test_cat_chat_file():
    """Read the main chat module successfully."""
    assert "Main entry point" in run_cat("chat.py")


def test_cat_decode_error_branch():
    """Catch read errors raised by the shared file loader."""
    with patch("tools.cat.read_text_file", side_effect=UnicodeDecodeError(
        "utf-8",
        b"\xff",
        0,
        1,
        "invalid start byte",
    )):
        assert "Error:" in run_cat("chat.py")


def test_grep_unsafe():
    """Reject unsafe grep globs."""
    assert run_grep("x", "..") == "Error: unsafe path"


def test_grep_match():
    """Find matching lines across the tool modules."""
    assert "def run_ls" in run_grep("def run_ls", "tools/*.py")


def test_grep_no_match():
    """Return an empty string when grep finds nothing."""
    assert run_grep("^zzzzzz_not_found_12345$", "tools/*.py") == ""


def test_calculate_basic():
    """Return JSON for successful calculations."""
    assert json.loads(run_calculate("3 * 4")) == {"result": 12}


def test_calculate_error():
    """Return JSON for calculation failures."""
    assert "error" in json.loads(run_calculate("hello"))


def test_compact():
    """Rewrite a chat history into a compact summary."""
    chat = Chat()
    chat.messages = [{"role": "user", "content": "hello"}]
    result = run_compact(chat)
    assert result.startswith("Summary of conversation:")
    assert chat.messages[0]["role"] == "system"


def test_grep_exception_branch():
    """Skip unreadable files while continuing the search."""
    with patch("glob.glob", return_value=["fakefile.txt"]):
        with patch("tools.grep.read_text_file", side_effect=Exception("boom")):
            assert run_grep("x", "*.txt") == ""
