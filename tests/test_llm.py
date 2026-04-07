"""
test_llm.py - Simple doctest for LLM

>>> from docsum_pkg.llm import LLM
>>> llm = LLM()
>>> llm.chat("Say hello")
'Hello from LLM'
>>> llm.chat_with_system("System prompt", "User prompt")
'Hello from LLM'
>>> llm.stream_chat("Stream this")  # doctest: +ELLIPSIS
Hi!
<BLANKLINE>
"""

# no code needed, doctests handle all