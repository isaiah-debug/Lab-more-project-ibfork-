from docsum_pkg.docsum import summarize_text
from docsum_pkg.llm import LLM
from docsum_pkg.chat import Chat, repl

def test_summarize_text():
    """Test the summarization function with mock LLM output."""
    result = summarize_text("Python is awesome.")
    # Your current mock LLM returns "Hello from LLM"
    assert result == "Hello from LLM"

def test_repl(monkeypatch, capsys):
    """Test the REPL loop for full coverage."""
    inputs = iter(["Hello", "How are you?", "Goodbye"])

    def fake_input(prompt):
        try:
            return next(inputs)
        except StopIteration:
            raise KeyboardInterrupt

    repl(input_func=fake_input)

    captured = capsys.readouterr()
    # Confirm all expected responses appear
    assert "Hello! 👋 How can I assist you today?" in captured.out
    assert "You said: How are you?" in captured.out
    assert "Goodbye!" in captured.out