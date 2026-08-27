from __future__ import annotations

from decimal import Decimal
from typing import Any


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


def mi_herramienta(connection: Any, limite: int = 10) -> list[dict[str, Any]]:
    """Reemplazar por una descripción clara del resultado que entrega."""
    if not 1 <= limite <= 100:
        raise ValueError("limite debe estar entre 1 y 100.")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id_cliente, venta_total
            FROM ventas_online
            ORDER BY venta_total DESC
            LIMIT %s;
            """,
            (limite,),
        )
        columns = [description[0] for description in cursor.description]
        return [
            {
                column: _json_safe(value)
                for column, value in zip(columns, row)
            }
            for row in cursor.fetchall()
        ]


TOOL_DEFINITIONS = [
    {
        "name": "personaN_mi_herramienta",
        "description": "Reemplazar por una descripción útil para el agente.",
        "parameters": {
            "limite": {"type": "integer", "default": 10}
        },
        "handler": mi_herramienta,
    }
]
