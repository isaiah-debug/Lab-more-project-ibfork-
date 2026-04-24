# Local Project Chat Agent

An AI-powered command-line agent for exploring and analyzing local codebases using natural language and LLM-based tool calling. It provides safe access to files through built-in tools like `ls`, `cat`, `grep`, `calculate`, and `compact`.

![doctests](https://img.shields.io/github/actions/workflow/status/MiaUrosevic/Lab-more-project/doctests.yml?label=doctests)
![integration-tests](https://img.shields.io/github/actions/workflow/status/MiaUrosevic/Lab-more-project/integration-tests.yml?label=integration-tests)
![flake8](https://img.shields.io/github/actions/workflow/status/MiaUrosevic/Lab-more-project/flake8.yml?label=flake8)
![coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)
![pypi](https://img.shields.io/pypi/v/lab-more-project-chat)

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

```bash
pip install -r requirements.txt
```

## Usage

```bash
python chat.py
python chat.py "what is 2 + 2?"
python chat.py --debug "what files are in the .github folder?"
python chat.py --provider groq "show me README.md"
```

## Example: Webscraping Project
This example is good because it shows the agent answering a high-level question about a real scraping project.

```bash
$ cd test_projects/webscraping_project
$ python ../../chat.py "what is this project about?"
The project is designed to scrape product data from eBay listings, including titles, prices, and links.
```

## Example: Markdown Compiler
This example is good because it shows the agent inspecting implementation details across source files.

```bash
$ cd test_projects/markdown_compiler
$ python ../../chat.py "find def in *.py"
def compile_markdown(file_path):
def parse_headers(text):
def render_html(content):
```

## Example: Mia.Urosevic.github.io
This example is good because it shows the agent reading and summarizing files from a real webpage project.

```bash
$ cd test_projects/Mia.Urosevic.github.io
$ python ../../chat.py "show me README.md"
This project is a personal website built using HTML, CSS, and JavaScript.
```
