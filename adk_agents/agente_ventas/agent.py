from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


AGENTS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_SERVER_DIR = REPO_ROOT / "mcp_server"
MCP_SERVER_PATH = MCP_SERVER_DIR / "server.py"
MCP_PYTHON = (
    MCP_SERVER_DIR / ".venv" / "Scripts" / "python.exe"
    if os.name == "nt"
    else MCP_SERVER_DIR / ".venv" / "bin" / "python"
)

load_dotenv(AGENTS_DIR / ".env")

if not MCP_PYTHON.exists():
    raise FileNotFoundError(
        "No existe el entorno del MCP Server. Instala mcp_server/requirements.txt."
    )


mcp_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=str(MCP_PYTHON),
            args=[str(MCP_SERVER_PATH)],
            env=dict(os.environ),
        ),
        timeout=20,
    )
)


root_agent = LlmAgent(
    model=os.getenv("GOOGLE_MODEL", "gemini-flash-latest"),
    name="analista_ventas_grupo10",
    description="Agente conversacional para analizar las ventas del Grupo 10.",
    instruction="""
Eres el analista conversacional del Grupo 10 para la Práctica 1 de SOG2.

Reglas:
1. Usa las herramientas MCP para responder preguntas sobre los datos.
2. No inventes cifras ni presentes estimaciones como resultados exactos.
3. Indica claramente la métrica usada: clientes, compras, ventas o tiempo.
4. Explica los resultados en español, con lenguaje claro y profesional.
5. Si una herramienta no cubre la pregunta, indícalo en lugar de improvisar.
6. Cuando compares grupos, menciona valores y no solamente conclusiones.
""".strip(),
    tools=[mcp_tools],
)
