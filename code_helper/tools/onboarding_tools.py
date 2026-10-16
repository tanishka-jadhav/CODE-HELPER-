"""
code_helper/tools/onboarding_tools.py — Onboarding & Architecture Orientation Tool.
"""
from pathlib import Path
from code_helper.config import config


def get_project_quickstart_and_modules() -> str:
    """
    Returns project purpose, file reading order, and run commands for new developers.
    """
    guide = [
        "Naive_RAG Project Onboarding Guide:",
        "1. Purpose: A reference 8-stage RAG system using NVIDIA NIM and Pinecone.",
        "2. Recommended Reading Order:",
        "   - config.py (Settings & credentials)",
        "   - indexer.py (Offline indexing: Read -> Split -> Embed -> Store)",
        "   - vector_store.py (Pinecone client and cosine similarity)",
        "   - query_pipeline.py (Online query: Embed -> Retrieve -> Augment -> Generate)",
        "   - main.py (Interactive CLI demonstration)",
        "3. Run Commands:",
        "   - Full Demo: python main.py",
        "   - Indexing Only: python main.py --index",
        "   - Custom Query: python main.py --query '<question>'",
        "   - Compare: python main.py --compare",
        "\n[ONBOARDING GUIDE COMPLETE]: Provide these exact details directly to the user. Do not call any further tools.",
    ]
    return "\n".join(guide)
