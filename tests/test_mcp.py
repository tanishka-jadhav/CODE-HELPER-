"""
tests/test_mcp.py — Verification of Filesystem MCP Server connection via ADK McpToolset.
"""
import asyncio
import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_helper.config import config
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


async def main():
    print("=" * 65)
    print("TESTING MCP FILESYSTEM SERVER CONNECTION (NODE/NPX)")
    print("=" * 65)

    npx_cmd = shutil.which("npx") or "npx"
    target_path = str(config.target_codebase_dir.resolve().as_posix())
    
    print(f"[*] npx command path: {npx_cmd}")
    print(f"[*] Target directory: {target_path}")

    file_tools = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=npx_cmd,
                args=["-y", "@modelcontextprotocol/server-filesystem", target_path],
            ),
            timeout=30,
        ),
        tool_filter=["list_directory", "read_file"],
    )

    print("[*] Connecting to MCP server via stdio transport...")
    tools = await file_tools.get_tools()
    tool_names = [t.name for t in tools]
    
    print("\n" + "-" * 65)
    print(f"[OK] MCP Server connected successfully!")
    print(f"[*] Exposed Tools ({len(tools)}): {tool_names}")
    for t in tools:
        print(f"  -> {t.name}: {t.description[:80]}...")
    print("-" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
