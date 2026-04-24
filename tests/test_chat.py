"""Unit tests for chat session behavior and command routing."""

import json
from unittest.mock import patch

from chat import Chat, is_path_safe, main, repl


def test_is_path_safe():
    """Reject absolute and traversal paths while allowing safe relative paths."""
    assert is_path_safe("README.md") is True
    assert is_path_safe("/etc/passwd") is False
    assert is_path_safe("../x") is False
    assert is_path_safe("a/../b.txt") is False
    assert is_path_safe(r"C:\Windows\System32") is False


def test_execute_tool_call():
    """Execute a tutorial-shaped tool call payload locally."""
    chat = Chat()
    tool_call = chat._make_tool_call("calculate", {"expression": "5 + 7"})
    command, result, args = chat.execute_tool_call(tool_call)
    assert command == "calculate"
    assert json.loads(result) == {"result": 12}
    assert args == ["5 + 7"]


def test_unknown_manual_command():
    """Return a clear error for unsupported slash commands."""
    chat = Chat()
    assert chat.run_manual_command("/notreal") == "Error: unknown command 'notreal'"


def test_manual_ls_returns_string():
    """Allow ls to run without an explicit argument."""
    chat = Chat()
    result = chat.run_manual_command("/ls")
    assert isinstance(result, str)


def test_manual_cat_wrong_args():
    """Reject cat calls that do not include a path."""
    chat = Chat()
    assert chat.run_manual_command("/cat") == "Error: cat requires 1 argument"


def test_manual_grep_wrong_args():
    """Reject grep calls without both required parameters."""
    chat = Chat()
    assert chat.run_manual_command("/grep x") == "Error: grep requires 2 arguments"


def test_manual_calculate_wrong_args():
    """Reject calculate calls without an expression."""
    chat = Chat()
    assert (
        chat.run_manual_command("/calculate")
        == "Error: calculate requires 1 argument"
    )


def test_manual_command_records_tool_output():
    """Store manual tool output in the chat transcript."""
    chat = Chat()
    chat.run_manual_command("/calculate 2+2")
    assert chat.messages[-1]["role"] == "tool"
    assert "/calculate 2+2" in chat.messages[-1]["content"]


def test_auto_choose_ls():
    """Route folder questions to the ls tool."""
    chat = Chat()
    tool_call = chat._auto_choose_tool("what files are in the .github folder?")
    assert tool_call["function"]["name"] == "ls"
    assert json.loads(tool_call["function"]["arguments"]) == {"path": ".github"}


def test_auto_choose_cat():
    """Route file-opening prompts to the cat tool."""
    chat = Chat()
    tool_call = chat._auto_choose_tool("show me README.md")
    assert tool_call["function"]["name"] == "cat"
    assert json.loads(tool_call["function"]["arguments"]) == {"path": "README.md"}


def test_auto_choose_grep():
    """Route search prompts to the grep tool."""
    chat = Chat()
    tool_call = chat._auto_choose_tool("find def run_ls in tools/*.py")
    assert tool_call["function"]["name"] == "grep"
    assert json.loads(tool_call["function"]["arguments"]) == {
        "pattern": "def run_ls",
        "path_glob": "tools/*.py",
    }


def test_auto_choose_calculate():
    """Route arithmetic prompts to the calculate tool."""
    chat = Chat()
    tool_call = chat._auto_choose_tool("what is 5 + 7?")
    assert tool_call["function"]["name"] == "calculate"
    assert json.loads(tool_call["function"]["arguments"]) == {"expression": "5 + 7"}


def test_auto_choose_none():
    """Leave unrelated prompts unanswered by the tool router."""
    chat = Chat()
    assert chat._auto_choose_tool("tell me something interesting") is None


def test_send_message_calculate():
    """Return the parsed calculation answer for automatic tool use."""
    chat = Chat()
    assert chat.send_message("what is 5 + 7?") == "12"


def test_send_message_unknown():
    """Return the fallback message when no tool is selected."""
    chat = Chat()
    result = chat.send_message("tell me something interesting")
    assert "I could not automatically determine" in result


def test_send_message_ls_empty_branch():
    """Handle empty directory listings cleanly."""
    chat = Chat()
    with patch.dict(chat.tools["ls"], {"runner": lambda path=".": ""}):
        result = chat.send_message("what files are in the .github folder?")
    assert result == "That folder appears to be empty."


def test_send_message_ls_multiple_branch():
    """Summarize multiple listed files in the automatic response."""
    chat = Chat()
    with patch.dict(chat.tools["ls"], {"runner": lambda path=".": "a\nb"}):
        result = chat.send_message("what files are in the .github folder?")
    assert result == "The files in that folder are: a, b."


def test_manual_compact():
    """Allow compact to rewrite the chat history through a slash command."""
    chat = Chat()
    chat.messages.append({"role": "user", "content": "hello"})
    result = chat.run_manual_command("/compact")
    assert result.startswith("Summary of conversation:")


def test_main_one_shot():
    """Run the one-shot CLI path without error."""
    assert main(["what is 2 + 2?"]) is None


def test_repl_keyboard_interrupt(capsys):
    """Exit the REPL cleanly on Ctrl-C."""
    chat = Chat()
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        repl(chat)
    captured = capsys.readouterr()
    assert captured.out == "\n"


def test_repl_slash_command(capsys):
    """Execute slash commands directly inside the REPL."""
    chat = Chat()
    with patch("builtins.input", side_effect=["/calculate 2+2", KeyboardInterrupt]):
        repl(chat)
    captured = capsys.readouterr()
    assert '{"result": 4}' in captured.out


def test_repl_normal_message(capsys):
    """Use automatic tool routing inside the REPL."""
    chat = Chat()
    with patch("builtins.input", side_effect=["what is 2 + 2?", KeyboardInterrupt]):
        repl(chat)
    captured = capsys.readouterr()
    assert "4" in captured.out
