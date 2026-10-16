"""
test_embeddings.py — Pre-flight verification for NVIDIA NIM Embedding API.
Verifies credentials and confirms exact output dimensionality (expected: 2048).
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load .env from project root
root_dir = Path(__file__).resolve().parent.parent
env_file = root_dir / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

# 2. Validate API key presence without printing secret values
api_key = os.getenv("NVIDIA_API_KEY", "").strip()
if not api_key:
    api_key = os.getenv("NVIDIA_NIM_API_KEY", "").strip()

if not api_key or "your-key-here" in api_key:
    print("[ERROR] Neither NVIDIA_API_KEY nor NVIDIA_NIM_API_KEY found in .env!")
    print("Please ensure your .env file exists and contains your real NVIDIA API key.")
    sys.exit(1)

base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").strip()
embed_model = os.getenv("NVIDIA_EMBED_MODEL", "nvidia/nemotron-3-embed-1b").strip()

print("=" * 60)
print("PRE-FLIGHT CHECK: NVIDIA NIM EMBEDDING API")
print("=" * 60)
print(f"[*] Base URL       : {base_url}")
print(f"[*] Model ID       : {embed_model}")
print(f"[*] API Key Status : PRESENT (Masked per Security Policy)")

# 3. Call Embedding API with a sample text probe
try:
    client = OpenAI(base_url=base_url, api_key=api_key)
    sample_text = "def hello_world(): return 'Hello GenAI Engineer'"
    
    print(f"[*] Sending probe string to NVIDIA NIM...")
    response = client.embeddings.create(
        input=[sample_text],
        model=embed_model,
    )
    
    vector = response.data[0].embedding
    dim = len(vector)
    
    print("\n" + "-" * 60)
    print(f"[OK] Embedding API call succeeded!")
    print(f"[*] Measured Vector Dimension : {dim}")
    print(f"[*] Expected Vector Dimension : 2048")
    
    if dim == 2048:
        print("[VERIFIED] Real vector dimension MATCHES Pinecone specification (2048).")
    else:
        print(f"[WARNING] Dimension mismatch! Expected 2048, got {dim}.")
    print("-" * 60 + "\n")

except Exception as err:
    print(f"\n[ERROR] Failed to connect to NVIDIA NIM: {err}")
    sys.exit(1)
