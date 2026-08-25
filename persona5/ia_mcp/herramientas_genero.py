from __future__ import annotations

from decimal import Decimal
from typing import Any, Callable

RESUMEN_GENERO_QUERY = """
SELECT
    CASE genero WHEN 1 THEN 'Femenino' WHEN 0 THEN 'Masculino' END AS genero,
    COUNT(*) AS total_clientes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje_clientes,
    SUM(n_compras) AS total_compras,
    ROUND(AVG(n_compras), 3) AS compras_media
FROM ventas_online
GROUP BY genero
ORDER BY genero
"""

ESTADISTICAS_N_COMPRAS_QUERY = """
SELECT
    ROUND(AVG(n_compras), 3) AS media,
    (PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY n_compras))::NUMERIC AS mediana,
    MODE() WITHIN GROUP (ORDER BY n_compras) AS moda
FROM ventas_online
{filtro_genero}
"""

METODO_PAGO_POR_GENERO_QUERY = """
SELECT
    CASE genero WHEN 1 THEN 'Femenino' WHEN 0 THEN 'Masculino' END AS genero,
    CASE metodo_pago
        WHEN 0 THEN 'Efectivo'
        WHEN 1 THEN 'Tarjeta de Crédito'
        WHEN 2 THEN 'Tarjeta de Débito'
    END AS metodo_pago,
    COUNT(*) AS clientes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY genero), 2) AS porcentaje_dentro_genero
FROM ventas_online
GROUP BY genero, metodo_pago
ORDER BY genero, metodo_pago
"""


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


def _execute(connection: Any, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        return [
            {column: _json_safe(value) for column, value in zip(columns, row)}
            for row in cursor.fetchall()
        ]


def resumen_genero(connection: Any) -> list[dict[str, Any]]:
    """Devuelve cantidad de clientes, total y promedio de compras por género."""
    return _execute(connection, RESUMEN_GENERO_QUERY)


def estadisticas_n_compras(connection: Any, genero: int | None = None) -> list[dict[str, Any]]:
    """Devuelve media, mediana y moda de N_Compras, opcionalmente filtrando por género (0/1)."""
    if genero is None:
        query = ESTADISTICAS_N_COMPRAS_QUERY.format(filtro_genero="")
        return _execute(connection, query)
    if genero not in (0, 1):
        raise ValueError("genero debe ser 0 (masculino), 1 (femenino) o None.")
    query = ESTADISTICAS_N_COMPRAS_QUERY.format(filtro_genero="WHERE genero = %s")
    return _execute(connection, query, (genero,))


def metodo_pago_por_genero(connection: Any) -> list[dict[str, Any]]:
    """Devuelve la distribución de método de pago dentro de cada género."""
    return _execute(connection, METODO_PAGO_POR_GENERO_QUERY)


TOOL_DEFINITIONS = [
    {
        "name": "resumen_genero",
        "description": "Compara cantidad de clientes, total y promedio de compras entre géneros.",
        "parameters": {},
        "handler": resumen_genero,
    },
    {
        "name": "estadisticas_n_compras",
        "description": "Media, mediana y moda de N_Compras, en general o filtrado por género.",
        "parameters": {"genero": {"type": "integer", "enum": [0, 1], "required": False}},
        "handler": estadisticas_n_compras,
    },
    {
        "name": "metodo_pago_por_genero",
        "description": "Distribución del método de pago preferido dentro de cada género.",
        "parameters": {},
        "handler": metodo_pago_por_genero,
    },
]


def dispatch_tool(connection: Any, name: str, arguments: dict[str, Any] | None = None) -> Any:
    """Despacha una herramienta por nombre para conectarla a un servidor MCP."""
    arguments = arguments or {}
    handlers: dict[str, Callable[..., Any]] = {
        tool["name"]: tool["handler"] for tool in TOOL_DEFINITIONS
    }
    if name not in handlers:
        available = ", ".join(sorted(handlers))
        raise ValueError(f"Herramienta desconocida: {name}. Disponibles: {available}")
    return handlers[name](connection, **arguments)
