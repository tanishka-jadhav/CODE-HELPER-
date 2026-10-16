"""
code_helper/tools/file_tools.py — Direct Codebase File Reading Tool.

Provides safe, sandboxed full-file reading for in-depth code explanation
prior to MCP server connection in Phase 11.
"""
from pathlib import Path
from code_helper.config import config


def read_code_file(file_name: str) -> str:
    """
    Reads the entire content of a Python file in the codebase.
    
    Use this tool whenever the user asks to explain a specific file in detail,
    walk through a script line-by-line, or review a module's complete implementation.
    
    Args:
        file_name: The name of the file to read (e.g. 'vector_store.py' or 'query_pipeline.py').
        
    Returns:
        The full, exact text content of the file with line numbers, or an error if not found.
    """
    cleaned = file_name.strip().replace("\\", "/")
    if cleaned.startswith("Naive_RAG/"):
        cleaned = cleaned[len("Naive_RAG/"):]

    target_path = (config.target_codebase_dir / cleaned).resolve()

    # Sandboxing: Ensure path is within Naive_RAG
    try:
        target_path.relative_to(config.target_codebase_dir.resolve())
    except ValueError:
        return f"Access Denied: Path '{file_name}' is outside the allowed project directory."

    if not target_path.exists() or not target_path.is_file():
        available = ", ".join(f.name for f in config.target_codebase_dir.glob("*.py"))
        return f"File '{file_name}' not found. Available Python files: {available}"

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"{i:>3} | {line.rstrip()}")

        header = f"=== FULL FILE CONTENT: {target_path.name} ({len(lines)} lines) ===\n"
        return header + "\n".join(numbered_lines)

    except Exception as err:
        return f"Error reading file '{file_name}': {str(err)}"
