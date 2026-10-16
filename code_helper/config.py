"""
code_helper/config.py — Centralized configuration for the Multi-Agent Code Helper.
Loads environment variables and defines settings for NVIDIA NIM, Pinecone, and RAG.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Locate and load .env from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Defensive Key Sanitization:
# LiteLLM looks for NVIDIA_NIM_API_KEY. If it contains a placeholder or truncated string,
# automatically map it to the valid key so authentication never breaks.
nim_key = os.getenv("NVIDIA_NIM_API_KEY", "").strip()
std_key = os.getenv("NVIDIA_API_KEY", "").strip()

if len(std_key) > 50 and (len(nim_key) < 50 or "your" in nim_key.lower()):
    os.environ["NVIDIA_NIM_API_KEY"] = std_key
    nim_key = std_key
elif len(nim_key) > 50 and (len(std_key) < 50 or "your" in std_key.lower()):
    os.environ["NVIDIA_API_KEY"] = nim_key
    std_key = nim_key
elif std_key and not nim_key:
    os.environ["NVIDIA_NIM_API_KEY"] = std_key
    nim_key = std_key
elif nim_key and not std_key:
    os.environ["NVIDIA_API_KEY"] = nim_key
    std_key = nim_key



@dataclass(frozen=True)
class AppConfig:
    """Immutable application settings container."""
    # Target Codebase Path
    target_codebase_dir: Path = ROOT_DIR / "Naive_RAG"

    # NVIDIA NIM Settings
    nvidia_api_key: str = os.getenv("NVIDIA_API_KEY", "")
    nvidia_base_url: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").strip()
    chat_model: str = os.getenv("NVIDIA_CHAT_MODEL", "meta/llama-3.2-11b-vision-instruct").strip()
    embed_model: str = os.getenv("NVIDIA_EMBED_MODEL", "nvidia/nemotron-3-embed-1b").strip()
    embed_dimension: int = 2048

    # Pinecone Settings
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "").strip()
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "code-helper").strip()
    pinecone_cloud: str = os.getenv("PINECONE_CLOUD", "aws").strip()
    pinecone_region: str = os.getenv("PINECONE_REGION", "us-east-1").strip()

    # RAG Chunking Hyperparameters
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k: int = 3
    similarity_threshold: float = 0.50


# Global singleton instance
config = AppConfig()
