# docsum.py
"""
docsum.py - Simple text summarization using LLM

Doctests:
>>> from docsum_pkg import summarize_text
>>> summarize_text("Python is a programming language used for AI and data science.")  # doctest: +ELLIPSIS
'Hello from LLM'
"""

from .llm import LLM  # only relative import

def summarize_text(text: str) -> str:
    """Summarize a given text using the LLM."""
    llm = LLM()
    return llm.chat(f"Summarize this in one sentence:\n{text}")