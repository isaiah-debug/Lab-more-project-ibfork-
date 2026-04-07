from .llm import LLM
from .docsum import summarize_text

"""
chat.py - Simple chat interface

Doctests for repl():
>>> import builtins
>>> inputs = ['Hello', 'How are you?', 'Goodbye']
>>> def monkey_input(prompt):
...     try:
...         response = inputs.pop(0)
...         print(f'{prompt}{response}')
...         return response
...     except IndexError:
...         raise KeyboardInterrupt
>>> repl(input_func=monkey_input)  # doctest: +ELLIPSIS
chat> Hello
Hello! 👋 How can I assist you today?
chat> How are you?
You said: How are you?
chat> Goodbye
Goodbye! If you ever need assistance again, feel free to reach out. Have a great day!
<BLANKLINE>
"""

class Chat:
    """A simple chat class with canned responses."""

    def send_message(self, message: str) -> str:
        """Return a canned response based on the input."""
        if "hello" in message.lower() or "hi" in message.lower():
            return "Hello! 👋 How can I assist you today?"
        elif "goodbye" in message.lower() or "bye" in message.lower():
            return "Goodbye! If you ever need assistance again, feel free to reach out. Have a great day!"
        else:
            return f"You said: {message}"

def repl(input_func=input):
    """Run a read-eval-print loop for the Chat class.
    Accepts a custom input function to allow testing.
    """
    chat = Chat()
    try:
        while True:
            user_input = input_func('chat> ')
            response = chat.send_message(user_input)
            print(response)
    except KeyboardInterrupt:
        # Ensure this line executes for coverage
        print()

# Only run REPL when this file is executed directly
if __name__ == '__main__':
    repl()