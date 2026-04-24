"""
The compact tool summarizes the current chat history into a short replacement message.
"""


TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "compact",
        "description": "Summarize the current chat history and replace it with the summary.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}


def run_compact(chat):
    """
    Replace the current chat history with a compact summary.

    >>> class DummyChat:
    ...     def __init__(self, provider="groq", debug=False):
    ...         self.messages = [
    ...             {"role": "user", "content": "hello"},
    ...             {"role": "assistant", "content": "hi there"}
    ...         ]
    ...         self.provider = provider
    ...         self.debug = debug
    ...     def build_summary(self, messages=None):
    ...         active = self.messages if messages is None else messages
    ...         first = active[0]["content"]
    ...         return f"Summary of conversation:\\n{first}"
    >>> chat = DummyChat()
    >>> result = run_compact(chat)
    >>> result.startswith("Summary of conversation:")
    True
    >>> len(chat.messages)
    1
    >>> chat.messages[0]["role"]
    'system'
    >>> "hello" in chat.messages[0]["content"]
    True
    """
    summarizer = chat.__class__(provider=chat.provider, debug=chat.debug)
    summary = summarizer.build_summary(chat.messages)
    chat.messages = [{"role": "system", "content": summary}]
    return summary
