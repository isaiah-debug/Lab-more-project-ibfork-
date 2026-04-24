"""Integration tests for the CLI and real project directories."""

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHAT_SCRIPT = REPO_ROOT / "chat.py"


def test_cli_message_runs():
    """Return a one-shot calculation answer from the CLI."""
    result = subprocess.run(
        [sys.executable, str(CHAT_SCRIPT), "what is 2 + 2?"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "4"


def test_cli_debug_runs():
    """Show debug output for automatic tool calls."""
    result = subprocess.run(
        [sys.executable, str(CHAT_SCRIPT), "--debug", "what is 2 + 2?"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0
    assert "[tool] /calculate 2 + 2" in result.stdout
    assert result.stdout.strip().endswith("4")


def test_cli_provider_runs():
    """Accept the provider flag while still answering normally."""
    result = subprocess.run(
        [sys.executable, str(CHAT_SCRIPT), "--provider", "groq", "what is 2 + 2?"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "4"


def test_repl_manual_command_runs():
    """Run slash commands directly through the interactive REPL."""
    result = subprocess.run(
        [sys.executable, str(CHAT_SCRIPT)],
        input="/ls .github\n",
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0
    assert "workflows" in result.stdout


def test_submodules_are_checked_out():
    """Populate the assignment's test_projects submodules in the repository."""
    for folder_name in [
        "webscraping_project",
        "markdown_compiler",
        "Mia.Urosevic.github.io",
    ]:
        project_dir = REPO_ROOT / "test_projects" / folder_name
        assert project_dir.exists()
        assert any(project_dir.iterdir())


def test_chat_runs_in_markdown_submodule():
    """Run the chat tool inside a previous project submodule."""
    project_dir = REPO_ROOT / "test_projects" / "markdown_compiler"
    result = subprocess.run(
        [sys.executable, str(CHAT_SCRIPT), "show me README.md"],
        capture_output=True,
        text=True,
        cwd=project_dir,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip()
