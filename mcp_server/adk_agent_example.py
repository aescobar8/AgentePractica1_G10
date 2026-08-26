from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


SERVER_PATH = Path(__file__).resolve().parent / "server.py"
SERVER_VENV = Path(__file__).resolve().parent / ".venv"
DEFAULT_SERVER_PYTHON = (
    SERVER_VENV / "Scripts" / "python.exe"
    if os.name == "nt"
    else SERVER_VENV / "bin" / "python"
)
SERVER_PYTHON = os.getenv("MCP_SERVER_PYTHON", str(DEFAULT_SERVER_PYTHON))

root_agent = LlmAgent(
    model=os.getenv("GOOGLE_MODEL", "gemini-flash-latest"),
    name="analista_ventas_grupo10",
    instruction=(
        "Eres un analista de datos. Utiliza las herramientas MCP para responder "
        "preguntas sobre los datos de ventas y explica claramente los resultados."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=SERVER_PYTHON,
                    args=[str(SERVER_PATH)],
                    env=dict(os.environ),
                ),
                timeout=15,
            )
        )
    ],
)
