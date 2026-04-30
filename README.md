# Local Project Chat Agent

This command-line chat agent explores local codebases with natural language and tool calls. It provides safe access to files through built-in tools like `ls`, `cat`, `grep`, `calculate`, and `compact`.

![doctests](https://img.shields.io/github/actions/workflow/status/isaiah-debug/Lab-more-project-ibfork-/doctests.yml?label=doctests)
![integration-tests](https://img.shields.io/github/actions/workflow/status/isaiah-debug/Lab-more-project-ibfork-/integration-tests.yml?label=integration-tests)
![flake8](https://img.shields.io/github/actions/workflow/status/isaiah-debug/Lab-more-project-ibfork-/flake8.yml?label=flake8)

---

## Demo

![demo](demo.gif)

---

## Features

- Safe local file inspection with path validation (prevents absolute paths and traversal attacks)
- Manual slash commands (`/ls`, `/cat`, `/grep`, `/calculate`, `/compact`)
- Automatic **LLM-based tool calling**
- One-shot CLI usage
- `--debug` flag to display tool calls
- `--provider` flag for model selection
- Full testing suite (doctests, integration tests, flake8, coverage)

---

## Installation

Install the project dependencies before running the chat script:

```bash
$ pip install -r requirements.txt
```

## Usage

Run the interactive chat or pass a one-shot message from the terminal:

```bash
$ python chat.py
chat> what is 2 + 2?
4

$ python chat.py "what is 2 + 2?"
4

$ python chat.py --debug "what files are in the .github folder?"
[tool] /ls .github
The only file in that folder is workflows.

$ python chat.py --provider groq "show me README.md"
# Local Project Chat Agent
```

## Example: Webscraping Project

The agent can answer high-level questions about a real scraping project:

```bash
$ cd test_projects/webscraping_project
$ python ../../chat.py "what is this project about?"
The project is designed to scrape product data from eBay listings, including titles, prices, and links.
```

## Example: Markdown Compiler

The agent can inspect implementation details across source files:

```bash
$ cd test_projects/markdown_compiler
$ python ../../chat.py "find def in *.py"
def compile_markdown(file_path):
def parse_headers(text):
def render_html(content):
```

## Example: Mia.Urosevic.github.io

The agent can read and summarize files from a webpage project:

```bash
$ cd test_projects/Mia.Urosevic.github.io
$ python ../../chat.py "show me README.md"
This project is a personal website built using HTML, CSS, and JavaScript.
```
