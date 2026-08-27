from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, dict[str, Any]]
    handler: Callable[..., Any]
    owner: str
    source: Path


def _load_module(path: Path, index: int) -> ModuleType:
    module_name = f"grupo10_mcp_plugin_{path.parent.parent.name}_{index}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo MCP: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover_tools(repo_root: Path) -> list[ToolSpec]:
    """Descubre persona*/ia_mcp/herramientas_*.py y valida sus herramientas."""
    paths = sorted(repo_root.glob("persona*/ia_mcp/herramientas_*.py"))
    tools: list[ToolSpec] = []
    names: dict[str, Path] = {}

    for index, path in enumerate(paths):
        module = _load_module(path, index)
        definitions = getattr(module, "TOOL_DEFINITIONS", None)
        if not isinstance(definitions, list):
            raise ValueError(f"{path} debe exponer una lista TOOL_DEFINITIONS.")

        owner = path.parent.parent.name
        for definition in definitions:
            if not isinstance(definition, dict):
                raise ValueError(f"Definición inválida en {path}: {definition!r}")

            name = definition.get("name")
            description = definition.get("description")
            parameters = definition.get("parameters", {})
            handler = definition.get("handler")

            if not isinstance(name, str) or not name:
                raise ValueError(f"Herramienta sin nombre válido en {path}.")
            if name in names:
                raise ValueError(
                    f"Nombre MCP duplicado '{name}' en {path} y {names[name]}."
                )
            if not isinstance(description, str) or not description:
                raise ValueError(f"'{name}' no contiene una descripción válida.")
            if not isinstance(parameters, dict):
                raise ValueError(f"'{name}' debe declarar parameters como diccionario.")
            if not callable(handler):
                raise ValueError(f"'{name}' no contiene un handler ejecutable.")

            names[name] = path
            tools.append(
                ToolSpec(
                    name=name,
                    description=description,
                    parameters=parameters,
                    handler=handler,
                    owner=owner,
                    source=path,
                )
            )

    return tools
