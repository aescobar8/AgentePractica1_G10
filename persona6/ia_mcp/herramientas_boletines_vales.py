from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable


SUMMARY_QUERY = """
SELECT
    COUNT(*) AS total_clientes,
    SUM(boletin) AS clientes_con_boletin,
    ROUND(100.0 * SUM(boletin) / NULLIF(COUNT(*), 0), 2) AS porcentaje_boletin,
    SUM(vale) AS clientes_con_vale,
    ROUND(100.0 * SUM(vale) / NULLIF(COUNT(*), 0), 2) AS porcentaje_vale,
    SUM(CASE WHEN boletin = 1 AND vale = 1 THEN 1 ELSE 0 END) AS clientes_con_ambos,
    SUM(CASE WHEN boletin = 0 AND vale = 0 THEN 1 ELSE 0 END) AS clientes_sin_promocion
FROM ventas_online
"""

MONTHLY_QUERY = """
SELECT
    EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes_num,
    TO_CHAR(DATE_TRUNC('month', fecha_compra), 'YYYY-MM') AS mes,
    COUNT(*) AS registros,
    SUM(boletin) AS boletines_usados,
    ROUND(100.0 * SUM(boletin) / NULLIF(COUNT(*), 0), 2) AS porcentaje_boletines,
    SUM(vale) AS vales_usados,
    ROUND(100.0 * SUM(vale) / NULLIF(COUNT(*), 0), 2) AS porcentaje_vales
FROM ventas_online
WHERE EXTRACT(YEAR FROM fecha_compra) = %s
GROUP BY mes_num, mes
ORDER BY mes_num
"""

PATTERNS_QUERY = """
SELECT
    CASE
        WHEN boletin = 1 AND vale = 1 THEN 'Ambos'
        WHEN boletin = 1 AND vale = 0 THEN 'Solo boletin'
        WHEN boletin = 0 AND vale = 1 THEN 'Solo vale'
        ELSE 'Ninguno'
    END AS segmento,
    COUNT(*) AS registros,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje_registros,
    ROUND(AVG(venta_total), 3) AS venta_total_media,
    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY venta_total))::NUMERIC, 3) AS venta_total_mediana,
    ROUND(AVG(n_compras), 3) AS compras_media,
    ROUND(AVG(monto_compra), 3) AS monto_compra_media
FROM ventas_online
GROUP BY segmento
ORDER BY CASE segmento
    WHEN 'Ninguno' THEN 1
    WHEN 'Solo boletin' THEN 2
    WHEN 'Solo vale' THEN 3
    WHEN 'Ambos' THEN 4
END
"""

RELATION_QUERY = """
SELECT
    boletin,
    vale,
    COUNT(*) AS registros,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje_total
FROM ventas_online
GROUP BY boletin, vale
ORDER BY boletin, vale
"""

RELATION_METRICS_QUERY = """
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN boletin = 1 AND vale = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN boletin = 1 THEN 1 ELSE 0 END), 0),
        2
    ) AS porcentaje_vale_dado_boletin,
    ROUND(
        100.0 * SUM(CASE WHEN boletin = 0 AND vale = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN boletin = 0 THEN 1 ELSE 0 END), 0),
        2
    ) AS porcentaje_vale_sin_boletin,
    CORR(boletin::NUMERIC, vale::NUMERIC) AS correlacion_phi
FROM ventas_online
"""


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _execute(connection: Any, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        return [
            {column: _json_safe(value) for column, value in zip(columns, row)}
            for row in cursor.fetchall()
        ]


def resumen_boletines_vales(connection: Any) -> list[dict[str, Any]]:
    """Devuelve el resumen total de uso de boletines, vales y ambas promociones."""
    return _execute(connection, SUMMARY_QUERY)


def uso_mensual_boletines_vales(
    connection: Any, year: int = 2021
) -> list[dict[str, Any]]:
    """Devuelve conteos y porcentajes mensuales para el año solicitado."""
    if not isinstance(year, int) or not 1900 <= year <= 2100:
        raise ValueError("year debe ser un entero entre 1900 y 2100.")
    return _execute(connection, MONTHLY_QUERY, (year,))


def patrones_compra_promociones(connection: Any) -> list[dict[str, Any]]:
    """Compara venta total, compras y monto de compra por segmento promocional."""
    return _execute(connection, PATTERNS_QUERY)


def relacion_boletin_vale(connection: Any) -> dict[str, Any]:
    """Devuelve la tabla Boletin x Vale y sus probabilidades condicionales."""
    return {
        "tabla": _execute(connection, RELATION_QUERY),
        "metricas": _execute(connection, RELATION_METRICS_QUERY),
    }


TOOL_DEFINITIONS = [
    {
        "name": "resumen_boletines_vales",
        "description": "Resume cuántos clientes utilizan boletines, vales, ambas promociones o ninguna.",
        "parameters": {},
        "handler": resumen_boletines_vales,
    },
    {
        "name": "uso_mensual_boletines_vales",
        "description": "Consulta el uso mensual de boletines y vales para un año.",
        "parameters": {"year": {"type": "integer", "default": 2021}},
        "handler": uso_mensual_boletines_vales,
    },
    {
        "name": "patrones_compra_promociones",
        "description": "Compara ventas, cantidad de compras y montos entre segmentos promocionales.",
        "parameters": {},
        "handler": patrones_compra_promociones,
    },
    {
        "name": "relacion_boletin_vale",
        "description": "Analiza la relación entre usar boletín y usar vale con conteos y probabilidades.",
        "parameters": {},
        "handler": relacion_boletin_vale,
    },
]


def dispatch_tool(
    connection: Any, name: str, arguments: dict[str, Any] | None = None
) -> Any:
    """Despacha una herramienta por nombre para conectarla a un servidor MCP."""
    arguments = arguments or {}
    handlers: dict[str, Callable[..., Any]] = {
        tool["name"]: tool["handler"] for tool in TOOL_DEFINITIONS
    }
    if name not in handlers:
        available = ", ".join(sorted(handlers))
        raise ValueError(f"Herramienta desconocida: {name}. Disponibles: {available}")
    return handlers[name](connection, **arguments)
