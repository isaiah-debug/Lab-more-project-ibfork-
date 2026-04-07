# Docsum Chat Project

![Doctests](https://github.com/MiaUrosevic/Lab-more-project/actions/workflows/doctests.yml/badge.svg)
![Integration Tests](https://github.com/MiaUrosevic/Lab-more-project/actions/workflows/integration-tests.yml/badge.svg)

## Project Description
This project provides a simple text summarization and chat interface using a mock LLM.  
- `chat.py` – A simple CLI chat program with canned responses.  
- `docsum.py` – Summarizes text using the LLM class.  
- `llm.py` – Mock LLM class used for testing and demonstration purposes.  

## Installation

Install via pip:

```bash
pip install cmc-csci40-mia

**Version management**  
   - Every time you update your package, increment the version in `pyproject.toml` (e.g., `0.1.1`, `0.2.0`, etc.).  
   - Rebuild and upload the new version:  

```bash
python -m build
twine upload dist/*