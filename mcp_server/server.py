from __future__ import annotations

import inspect
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server import MCPServer

from mcp_server.config import REPO_ROOT, get_connection, load_configuration
from mcp_server.registry import ToolSpec, discover_tools


load_configuration()
DISCOVERED_TOOLS = discover_tools(REPO_ROOT)

mcp = MCPServer(
    "sog2-grupo10-ventas",
    title="Análisis de ventas - Grupo 10",
    description=(
        "Herramientas de análisis sobre ventas, clientes, navegadores, género, "
        "boletines y vales almacenados en PostgreSQL."
    ),
    instructions=(
        "Usa las herramientas para responder con resultados calculados desde la "
        "base de datos. No inventes valores que no estén presentes en las respuestas."
    ),
)


def _python_type(parameter: dict[str, Any]) -> Any:
    type_map: dict[str, Any] = {
        "integer": int,
        "number": float,
        "string": str,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    annotation = type_map.get(parameter.get("type", "string"), Any)
    enum = parameter.get("enum")
   
    if isinstance(enum, list) and enum and all(isinstance(value, str) for value in enum):
        annotation = Literal.__getitem__(tuple(enum))
    if not parameter.get("required", True) and "default" not in parameter:
        annotation = annotation | None
    return annotation


def _create_tool_handler(tool: ToolSpec) -> Callable[..., Any]:
    def execute(**arguments: Any) -> Any:
        with get_connection() as connection:
            return tool.handler(connection, **arguments)

    execute.__name__ = tool.name
    execute.__doc__ = tool.description

    signature_parameters = []
    annotations: dict[str, Any] = {"return": Any}
    for name, definition in tool.parameters.items():
        annotation = _python_type(definition)
        annotations[name] = annotation
        if "default" in definition:
            default = definition["default"]
        elif definition.get("required", True):
            default = inspect.Parameter.empty
        else:
            default = None
        signature_parameters.append(
            inspect.Parameter(
                name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=annotation,
            )
        )

    execute.__annotations__ = annotations
    execute.__signature__ = inspect.Signature(
        parameters=signature_parameters,
        return_annotation=Any,
    )
    return execute


for discovered_tool in DISCOVERED_TOOLS:
    mcp.add_tool(
        _create_tool_handler(discovered_tool),
        name=discovered_tool.name,
        description=discovered_tool.description,
    )


@mcp.tool()
def listar_herramientas_del_grupo() -> list[dict[str, str]]:
    
    return [
        {
            "nombre": tool.name,
            "responsable": tool.owner,
            "descripcion": tool.description,
        }
        for tool in DISCOVERED_TOOLS
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
