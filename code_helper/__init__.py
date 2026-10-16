"""
code_helper/__init__.py — ADK Agent Package Entry Point.

Ensures .env is loaded into the process environment immediately when ADK CLI loads the package.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded into process environment immediately
root = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root / ".env")
load_dotenv()

# Mirror NVIDIA keys for LiteLLM compatibility
k1 = os.getenv("NVIDIA_API_KEY", "").strip()
k2 = os.getenv("NVIDIA_NIM_API_KEY", "").strip()

if len(k1) > 50 and (len(k2) < 50 or "your" in k2.lower()):
    os.environ["NVIDIA_NIM_API_KEY"] = k1
elif len(k2) > 50 and (len(k1) < 50 or "your" in k1.lower()):
    os.environ["NVIDIA_API_KEY"] = k2
elif k1 and not k2:
    os.environ["NVIDIA_NIM_API_KEY"] = k1
elif k2 and not k1:
    os.environ["NVIDIA_API_KEY"] = k2


from . import agent

__all__ = ["agent"]
