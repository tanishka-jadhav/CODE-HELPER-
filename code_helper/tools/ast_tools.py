"""
code_helper/tools/ast_tools.py — Plain Python AST Analysis Tools (No AI Guessing).
"""
import ast
import os
from pathlib import Path
from code_helper.config import config


def _normalize_file_path(file_name: str) -> Path:
    cleaned = file_name.strip().replace("\\", "/")
    if cleaned.startswith("Naive_RAG/"):
        cleaned = cleaned[len("Naive_RAG/"):]
    target = (config.target_codebase_dir / cleaned).resolve()
    try:
        target.relative_to(config.target_codebase_dir.resolve())
    except ValueError:
        raise PermissionError(f"Access denied: Path '{file_name}' resolves outside target codebase.")
    return target


def get_file_outline(file_name: str) -> str:
    """
    Extracts the structural outline of a Python file (classes, methods, functions, and lines).
    
    Args:
        file_name: Name of the Python file to inspect (e.g. 'indexer.py' or 'vector_store.py').
    """
    try:
        target_path = _normalize_file_path(file_name)
        if not target_path.exists() or not target_path.is_file():
            return f"Error: File '{file_name}' not found."

        with open(target_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=target_path.name)
        output_lines = [f"FILE OUTLINE: {target_path.name}"]

        docstring = ast.get_docstring(tree)
        if docstring:
            output_lines.append(f"Module Description: {docstring.strip().splitlines()[0]}")

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                output_lines.append(f"- Class: {node.name} (Lines {node.lineno}-{node.end_lineno})")
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        output_lines.append(f"    - Method: {item.name}() (Lines {item.lineno}-{item.end_lineno})")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                output_lines.append(f"- Function: {node.name}() (Lines {node.lineno}-{node.end_lineno})")

        output_lines.append("\n[AST OUTLINE COMPLETE]: Present this outline directly to the user. Do not call any additional tools.")
        return "\n".join(output_lines)
    except Exception as err:
        return f"Error parsing outline: {str(err)}"


def find_import_dependencies(target_module: str = "") -> str:
    """
    Finds which files import a given module and what each file imports.
    
    Args:
        target_module: Name of the module to inspect (e.g. 'config' or 'vector_store').
    """
    try:
        clean_target = target_module.strip()
        if clean_target.endswith(".py"):
            clean_target = clean_target[:-3]
        if clean_target.startswith("Naive_RAG/"):
            clean_target = clean_target[len("Naive_RAG/"):]

        py_files = sorted(list(config.target_codebase_dir.glob("*.py")))
        imported_by = {}

        for file_path in py_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            try:
                tree = ast.parse(content, filename=file_path.name)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_by.setdefault(alias.name, []).append((file_path.name, node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    mod_name = node.module or ""
                    imported_by.setdefault(mod_name, []).append((file_path.name, node.lineno))

        target = clean_target or "config"
        dependents = imported_by.get(target, [])

        output = [f"Files that import '{target}':"]
        if dependents:
            for fn, line in dependents:
                output.append(f"- {fn} (Line {line})")
        else:
            output.append(f"- No files import '{target}'")

        output.append("\n[DEPENDENCY SEARCH COMPLETE]: Report these matching files directly to the user. Do not call any further tools.")
        return "\n".join(output)
    except Exception as err:
        return f"Error analyzing imports: {str(err)}"


def get_codebase_tree(directory: str = "") -> str:
    """
    Lists all files and directories in the target codebase.
    """
    try:
        base_dir = config.target_codebase_dir
        lines = [f"Codebase Structure ({base_dir.name}):"]
        for item in sorted(base_dir.rglob("*.py")):
            rel = item.relative_to(base_dir)
            lines.append(f"- {rel.as_posix()}")
        lines.append("\n[CODEBASE TREE COMPLETE]: Present this directory structure directly to the user. Do not call any further tools.")
        return "\n".join(lines)
    except Exception as err:
        return f"Error generating tree: {str(err)}"
