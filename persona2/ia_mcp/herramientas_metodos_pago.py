from __future__ import annotations

from decimal import Decimal
from typing import Any


def _json_safe(valor: Any) -> Any:
    return float(valor) if isinstance(valor, Decimal) else valor


def _execute(connection: Any, consulta: str) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(consulta)
        columnas = [descripcion[0] for descripcion in cursor.description]
        return [
            {columna: _json_safe(valor) for columna, valor in zip(columnas, fila)}
            for fila in cursor.fetchall()
        ]


def resumen_metodos_pago(connection: Any) -> list[dict[str, Any]]:
    """Distribución, monto total y estadísticas por método de pago."""
    return _execute(
        connection,
        """
        SELECT
            metodo_pago,
            CASE metodo_pago
                WHEN 0 THEN 'Efectivo/contra entrega'
                WHEN 1 THEN 'Tarjeta de Crédito'
                WHEN 2 THEN 'Tarjeta de Débito'
            END AS nombre,
            COUNT(*) AS registros,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje,
            SUM(monto_compra) AS monto_total,
            ROUND(AVG(monto_compra), 3) AS media,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monto_compra) AS mediana
        FROM ventas_online
        WHERE metodo_pago IS NOT NULL AND monto_compra IS NOT NULL
        GROUP BY metodo_pago
        ORDER BY metodo_pago;
        """,
    )


def estadisticas_monto_compra(connection: Any) -> list[dict[str, Any]]:
    """Media, mediana, moda, mínimo y máximo general de MontoCompra."""
    return _execute(
        connection,
        """
        SELECT
            COUNT(*) AS registros,
            ROUND(AVG(monto_compra), 3) AS media,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monto_compra) AS mediana,
            MODE() WITHIN GROUP (ORDER BY monto_compra) AS moda,
            MIN(monto_compra) AS minimo,
            MAX(monto_compra) AS maximo
        FROM ventas_online
        WHERE monto_compra IS NOT NULL;
        """,
    )


def total_efectivo_contra_entrega(connection: Any) -> list[dict[str, Any]]:
    """Cantidad de registros y suma de MontoCompra pagada en efectivo."""
    return _execute(
        connection,
        """
        SELECT COUNT(*) AS registros, SUM(monto_compra) AS monto_total
        FROM ventas_online
        WHERE metodo_pago = 0 AND monto_compra IS NOT NULL;
        """,
    )


TOOL_DEFINITIONS = [
    {
        "name": "resumen_metodos_pago",
        "description": "Distribución de ventas, montos y comparación por método de pago.",
        "parameters": {},
        "handler": resumen_metodos_pago,
    },
    {
        "name": "estadisticas_monto_compra",
        "description": "Media, mediana, moda, mínimo y máximo general de MontoCompra.",
        "parameters": {},
        "handler": estadisticas_monto_compra,
    },
    {
        "name": "total_efectivo_contra_entrega",
        "description": "Total pagado mediante efectivo o contra entrega.",
        "parameters": {},
        "handler": total_efectivo_contra_entrega,
    },
]

