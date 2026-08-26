from __future__ import annotations

import asyncio
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp import Client

from mcp_server.server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print(f"Herramientas registradas: {len(tools.tools)}")
        for tool in tools.tools:
            print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
