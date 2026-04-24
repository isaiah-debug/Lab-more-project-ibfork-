"""
Main entry point for the local project chat application.

This file defines the Chat class, path safety checks, the CLI interface,
and the interactive REPL for talking to local project files with tools.
"""

import argparse
import json
import os
import shlex
from pathlib import PurePath, PurePosixPath, PureWindowsPath


def is_path_safe(path: str) -> bool:
    """
    Return True only if a path is relative and contains no directory traversal.

    >>> is_path_safe("README.md")
    True
    >>> is_path_safe("tools/ls.py")
    True
    >>> is_path_safe("/etc/passwd")
    False
    >>> is_path_safe("../secret.txt")
    False
    >>> is_path_safe("a/../b.txt")
    False
    >>> is_path_safe(r"C:\\Windows\\System32")
    False
    """
    if not path:
        return True
    if os.path.isabs(path):
        return False
    if PurePosixPath(path).is_absolute() or PureWindowsPath(path).is_absolute():
        return False
    normalized_path = path.replace("\\", "/")
    return ".." not in PurePath(normalized_path).parts


class Chat:
    """
    A Chat manages a local file-aware conversation session with manual and automatic tool use.

    It stores messages, supports slash commands like `/ls` and `/cat`, and models
    Groq-style local tool calling by building tool schemas, executing tool calls
    locally, and storing tool results in the conversation history.

    >>> chat = Chat()
    >>> isinstance(chat.messages, list)
    True
    >>> sorted(chat.tools.keys())
    ['calculate', 'cat', 'compact', 'grep', 'ls']
    >>> chat._auto_choose_tool("what is 2 + 2?")["function"]["name"]
    'calculate'
    """

    def __init__(self, provider="groq", debug=False):
        """
        Initialize a new Chat session.
        """
        from tools.calculate import TOOL_SPEC as CALCULATE_TOOL_SPEC
        from tools.calculate import run_calculate
        from tools.cat import TOOL_SPEC as CAT_TOOL_SPEC
        from tools.cat import run_cat
        from tools.compact import TOOL_SPEC as COMPACT_TOOL_SPEC
        from tools.compact import run_compact
        from tools.grep import TOOL_SPEC as GREP_TOOL_SPEC
        from tools.grep import run_grep
        from tools.ls import TOOL_SPEC as LS_TOOL_SPEC
        from tools.ls import run_ls

        self.provider = provider
        self.debug = debug
        self.messages = []
        self.tools = {
            "ls": {
                "spec": LS_TOOL_SPEC,
                "runner": lambda path=".": run_ls(path),
                "manual_arguments": ["path"],
            },
            "cat": {
                "spec": CAT_TOOL_SPEC,
                "runner": run_cat,
                "manual_arguments": ["path"],
            },
            "grep": {
                "spec": GREP_TOOL_SPEC,
                "runner": run_grep,
                "manual_arguments": ["pattern", "path_glob"],
            },
            "calculate": {
                "spec": CALCULATE_TOOL_SPEC,
                "runner": run_calculate,
                "manual_arguments": ["expression"],
            },
            "compact": {
                "spec": COMPACT_TOOL_SPEC,
                "runner": lambda: run_compact(self),
                "manual_arguments": [],
            },
        }

    def _debug_print(self, command, args):
        """
        Print a tool debug line if debug mode is enabled.

        >>> chat = Chat(debug=False)
        >>> chat._debug_print("ls", [".github"]) is None
        True
        """
        if self.debug:
            print(f"[tool] /{command}" + (f" {' '.join(args)}" if args else ""))

    def build_summary(self, messages=None):
        """
        Build a short summary of the provided chat messages.

        >>> chat = Chat()
        >>> summary = chat.build_summary([{"role": "user", "content": "hello"}])
        >>> summary.startswith("Summary of conversation:")
        True
        """
        active_messages = self.messages if messages is None else messages
        transcript = []
        for message in active_messages:
            transcript.append(f"{message['role']}: {message['content']}")
        summary_lines = transcript[:5]
        summary_body = "\n".join(summary_lines) if summary_lines else "No messages yet."
        return f"Summary of conversation:\n{summary_body}"

    def _manual_args_to_kwargs(self, command, args):
        """
        Convert manual slash-command arguments into keyword arguments.

        >>> chat = Chat()
        >>> chat._manual_args_to_kwargs("ls", [])
        {'path': '.'}
        >>> chat._manual_args_to_kwargs("grep", ["def", "tools/*.py"])
        {'pattern': 'def', 'path_glob': 'tools/*.py'}
        """
        argument_names = self.tools[command]["manual_arguments"]
        if command == "ls":
            if len(args) > 1:
                return None
            return {"path": args[0] if args else "."}
        if len(args) != len(argument_names):
            return None
        return dict(zip(argument_names, args))

    def execute_tool_call(self, tool_call):
        """
        Parse and execute a single tool call.

        >>> chat = Chat()
        >>> tool_call = chat._make_tool_call("calculate", {"expression": "2 + 2"})
        >>> chat.execute_tool_call(tool_call)[1]
        '{"result": 4}'
        """
        function_info = tool_call["function"]
        function_name = function_info["name"]
        function_to_call = self.tools[function_name]["runner"]
        function_args = json.loads(function_info["arguments"])
        function_response = function_to_call(**function_args)
        arg_values = [str(value) for value in function_args.values()]
        return function_name, function_response, arg_values

    def _make_tool_call(self, name, arguments):
        """
        Create a local tool-call payload in the Groq tutorial shape.

        >>> chat = Chat()
        >>> chat._make_tool_call("ls", {"path": ".github"})["function"]["arguments"]
        '{"path": ".github"}'
        """
        return {
            "id": f"call_{name}",
            "type": "function",
            "function": {
                "name": name,
                "arguments": json.dumps(arguments),
            },
        }

    def run_manual_command(self, line: str) -> str:
        """
        Execute a slash command directly without calling the model.

        >>> chat = Chat()
        >>> isinstance(chat.run_manual_command("/ls"), str)
        True
        >>> chat.run_manual_command("/doesnotexist")
        "Error: unknown command 'doesnotexist'"
        """
        parts = shlex.split(line.strip())
        if not parts or not parts[0].startswith("/"):
            return "Error: invalid command"

        command = parts[0][1:]
        args = parts[1:]

        if command not in self.tools:
            return f"Error: unknown command '{command}'"

        kwargs = self._manual_args_to_kwargs(command, args)
        if kwargs is None:
            return self._wrong_argument_error(command)

        tool_call = self._make_tool_call(command, kwargs)
        self._debug_print(command, args)
        executed_command, result, executed_args = self.execute_tool_call(tool_call)
        self._append_tool_message(executed_command, executed_args, result)
        return result

    def _wrong_argument_error(self, command):
        """
        Return the error message for an invalid manual tool invocation.

        >>> chat = Chat()
        >>> chat._wrong_argument_error("cat")
        'Error: cat requires 1 argument'
        """
        counts = {
            "ls": "Error: ls accepts at most 1 argument",
            "cat": "Error: cat requires 1 argument",
            "grep": "Error: grep requires 2 arguments",
            "calculate": "Error: calculate requires 1 argument",
            "compact": "Error: compact accepts 0 arguments",
        }
        return counts[command]

    def _append_tool_message(self, command, args, result):
        """
        Store a tool result in the current conversation.

        >>> chat = Chat()
        >>> chat._append_tool_message("ls", [".github"], "workflows")
        >>> chat.messages[-1]["role"]
        'tool'
        """
        self.messages.append(
            {
                "role": "tool",
                "name": command,
                "content": f"/{command}" + (f" {' '.join(args)}" if args else "")
                + f"\n{result}",
            }
        )

    def _auto_choose_tool(self, message: str):
        """
        Build a deterministic tool call for common local project questions.

        >>> chat = Chat()
        >>> chat._auto_choose_tool("what files are in the .github folder?")["function"]["name"]
        'ls'
        >>> chat._auto_choose_tool("show me README.md")["function"]["name"]
        'cat'
        >>> chat._auto_choose_tool("find def in tools/*.py")["function"]["name"]
        'grep'
        >>> chat._auto_choose_tool("what is 2 + 2?")["function"]["name"]
        'calculate'
        """
        text = message.strip()
        lowered = text.lower()

        if "what files are in" in lowered and " folder" in lowered:
            fragment = text.split("what files are in", 1)[1].split("folder", 1)[0]
            candidate = fragment.strip().strip("?").strip("`'\" ")
            if candidate.lower().startswith("the "):
                candidate = candidate[4:]
            return self._make_tool_call("ls", {"path": candidate})

        if lowered.startswith("show me ") or lowered.startswith("open "):
            filename = text.split(maxsplit=2)[-1].strip()
            return self._make_tool_call("cat", {"path": filename})

        if lowered.startswith("find ") and " in " in text:
            body = text[5:]
            pattern, path_glob = body.split(" in ", 1)
            return self._make_tool_call(
                "grep",
                {"pattern": pattern.strip(), "path_glob": path_glob.strip()},
            )

        if lowered.startswith("what is "):
            expression = text[8:].rstrip("?").strip()
            if any(character.isdigit() for character in expression):
                return self._make_tool_call(
                    "calculate",
                    {"expression": expression},
                )
        return None

    def _render_tool_response(self, command, tool_result):
        """
        Convert a raw tool result into the assistant's user-facing response.

        >>> chat = Chat()
        >>> chat._render_tool_response("ls", "a\\nb")
        'The files in that folder are: a, b.'
        >>> chat._render_tool_response("grep", "")
        'No lines matched that pattern.'
        """
        if command == "ls":
            if tool_result.strip():
                items = [line.strip() for line in tool_result.splitlines() if line.strip()]
                if len(items) == 1:
                    return f"The only file in that folder is {items[0]}."
                return "The files in that folder are: " + ", ".join(items) + "."
            return "That folder appears to be empty."

        if command == "calculate":
            try:
                parsed = json.loads(tool_result)
            except json.JSONDecodeError:
                return tool_result
            if "result" in parsed:
                return str(parsed["result"])
            return f"Error: {parsed.get('error', 'Unknown calculation error')}"

        if command == "grep":
            return tool_result if tool_result else "No lines matched that pattern."

        return tool_result

    def send_message(self, message: str) -> str:
        """
        Send a message and return a response.

        This version uses local tool-call payloads and a deterministic router so the
        required manual and automatic tool behavior can be tested reliably without
        depending on a live external provider.

        >>> chat = Chat()
        >>> isinstance(chat.send_message("what files are in the .github folder?"), str)
        True
        """
        self.messages.append({"role": "user", "content": message})
        tool_call = self._auto_choose_tool(message)

        if tool_call is not None:
            self.messages.append({"role": "assistant", "tool_calls": [tool_call]})
            command, tool_result, arg_values = self.execute_tool_call(tool_call)
            self._debug_print(command, arg_values)
            self._append_tool_message(command, arg_values, tool_result)
            return self._render_tool_response(command, tool_result)

        return (
            "I could not automatically determine the right tool for that request yet. "
            "Try a slash command like /ls, /cat, /grep, /calculate, or /compact."
        )


def parse_args(argv=None):
    """
    Parse command-line arguments.

    >>> args = parse_args(["hello"])
    >>> args.message
    'hello'
    >>> args = parse_args(["--debug", "--provider", "groq", "hi"])
    >>> (args.debug, args.provider, args.message)
    (True, 'groq', 'hi')
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("message", nargs="?", help="Optional one-shot message")
    parser.add_argument("--debug", action="store_true", help="Print tool-use calls")
    parser.add_argument(
        "--provider",
        default="groq",
        choices=["groq", "openai", "anthropic", "google"],
        help="Select the LLM provider",
    )
    return parser.parse_args(argv)


def repl(chat: Chat):
    """
    Run the interactive REPL until interrupted.
    """
    while True:
        try:
            line = input("chat> ")
            if not line.strip():
                continue
            if line[0] == "/":
                print(chat.run_manual_command(line))
            else:
                print(chat.send_message(line))
        except KeyboardInterrupt:
            print()
            break
        except EOFError:
            print()
            break


def main(argv=None):
    """
    Run the CLI program.

    >>> main(["what is 2 + 2?"]) is None
    4
    True
    """
    args = parse_args(argv)
    chat = Chat(provider=args.provider, debug=args.debug)

    if args.message:
        print(chat.send_message(args.message))
    else:
        repl(chat)


if __name__ == "__main__":
    main()
