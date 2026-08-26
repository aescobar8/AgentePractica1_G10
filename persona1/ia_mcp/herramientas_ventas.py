from __future__ import annotations

from decimal import Decimal
from typing import Any, Callable


MONTHLY_QUERY = """
SELECT
    EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes_num,
    TO_CHAR(DATE_TRUNC('month', fecha_compra), 'TMMonth') AS mes,
    COUNT(*) AS registros,
    ROUND(SUM(venta_total), 3) AS ventas_totales,
    ROUND(AVG(venta_total), 3) AS venta_media,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY venta_total) AS venta_mediana,
    MODE() WITHIN GROUP (ORDER BY venta_total) AS venta_moda
FROM ventas_online
WHERE EXTRACT(YEAR FROM fecha_compra) = %s
GROUP BY mes_num, mes
ORDER BY mes_num;
"""

SUMMARY_QUERY = """
SELECT
    COUNT(*) AS registros,
    ROUND(SUM(venta_total), 3) AS ventas_totales,
    ROUND(AVG(venta_total), 3) AS media,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY venta_total) AS mediana,
    MODE() WITHIN GROUP (ORDER BY venta_total) AS moda,
    MIN(venta_total) AS minimo,
    MAX(venta_total) AS maximo
FROM ventas_online;
"""

EXTREMES_QUERY = """
WITH mensual AS (
    SELECT
        EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes_num,
        TO_CHAR(DATE_TRUNC('month', fecha_compra), 'TMMonth') AS mes,
        SUM(venta_total) AS ventas_totales
    FROM ventas_online
    WHERE EXTRACT(YEAR FROM fecha_compra) = %s
    GROUP BY mes_num, mes
)
SELECT 'mayores_ventas' AS tipo, mes_num, mes, ventas_totales
FROM mensual
WHERE ventas_totales = (SELECT MAX(ventas_totales) FROM mensual)
UNION ALL
SELECT 'menores_ventas', mes_num, mes, ventas_totales
FROM mensual
WHERE ventas_totales = (SELECT MIN(ventas_totales) FROM mensual)
ORDER BY tipo, mes_num;
"""


def _json_safe(value: Any) -> Any:
    return float(value) if isinstance(value, Decimal) else value


def _execute(connection: Any, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        return [
            {column: _json_safe(value) for column, value in zip(columns, row)}
            for row in cursor.fetchall()
        ]


def resumen_ventas(connection: Any) -> list[dict[str, Any]]:
    """Devuelve estadísticas generales de Venta_total."""
    return _execute(connection, SUMMARY_QUERY)


def ventas_mensuales(connection: Any, year: int = 2021) -> list[dict[str, Any]]:
    """Devuelve ventas totales y estadísticas de Venta_total por mes."""
    if not isinstance(year, int) or not 1900 <= year <= 2100:
        raise ValueError("year debe ser un entero entre 1900 y 2100.")
    return _execute(connection, MONTHLY_QUERY, (year,))


def extremos_ventas_mensuales(connection: Any, year: int = 2021) -> list[dict[str, Any]]:
    """Identifica los meses con mayores y menores ventas totales."""
    if not isinstance(year, int) or not 1900 <= year <= 2100:
        raise ValueError("year debe ser un entero entre 1900 y 2100.")
    return _execute(connection, EXTREMES_QUERY, (year,))


TOOL_DEFINITIONS = [
    {
        "name": "resumen_ventas",
        "description": "Devuelve suma, media, mediana, moda, mínimo y máximo de Venta_total.",
        "parameters": {},
        "handler": resumen_ventas,
    },
    {
        "name": "ventas_mensuales",
        "description": "Consulta la distribución y evolución mensual de las ventas de un año.",
        "parameters": {"year": {"type": "integer", "default": 2021}},
        "handler": ventas_mensuales,
    },
    {
        "name": "extremos_ventas_mensuales",
        "description": "Encuentra los meses con mayores y menores ventas totales.",
        "parameters": {"year": {"type": "integer", "default": 2021}},
        "handler": extremos_ventas_mensuales,
    },
]


def dispatch_tool(
    connection: Any, name: str, arguments: dict[str, Any] | None = None
) -> Any:
    """Despacha una herramienta de Persona 1 por nombre."""
    arguments = arguments or {}
    handlers: dict[str, Callable[..., Any]] = {
        tool["name"]: tool["handler"] for tool in TOOL_DEFINITIONS
    }
    if name not in handlers:
        raise ValueError(f"Herramienta desconocida: {name}")
    return handlers[name](connection, **arguments)
