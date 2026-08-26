from __future__ import annotations

from decimal import Decimal
from typing import Any


NAVEGADOR_LABEL = {
    0: "Tienda Física",
    1: "Navegador 1",
    2: "Navegador 2",
    3: "Navegador 3",
    4: "Navegador 4",
}


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


def _execute(
    connection: Any, query: str, params: tuple[Any, ...] = ()
) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        return [
            {column: _json_safe(value) for column, value in zip(columns, row)}
            for row in cursor.fetchall()
        ]


def resumen_navegadores(connection: Any) -> list[dict[str, Any]]:
    """Resume clientes, compras y ventas por navegador."""
    return _execute(
        connection,
        """
        SELECT
            navegador,
            CASE navegador
                WHEN 0 THEN 'Tienda Física'
                ELSE 'Navegador ' || navegador
            END AS nombre,
            COUNT(*) AS clientes,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje,
            SUM(n_compras) AS total_compras,
            SUM(venta_total) AS ventas_totales
        FROM ventas_online
        GROUP BY navegador
        ORDER BY navegador;
        """,
    )


def estadisticas_tiempo(
    connection: Any, navegador: int | None = None
) -> list[dict[str, Any]]:
    """Calcula media, mediana, moda, mínimo y máximo de tiempo."""
    if navegador is not None and navegador not in NAVEGADOR_LABEL:
        raise ValueError("navegador debe estar entre 0 y 4, o ser None.")

    where = "" if navegador is None else "WHERE navegador = %s"
    params = () if navegador is None else (navegador,)
    return _execute(
        connection,
        f"""
        SELECT
            COUNT(*) AS registros,
            ROUND(AVG(tiempo), 2) AS media,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tiempo) AS mediana,
            MODE() WITHIN GROUP (ORDER BY tiempo) AS moda,
            MIN(tiempo) AS minimo,
            MAX(tiempo) AS maximo
        FROM ventas_online
        {where};
        """,
        params,
    )


def comparar_tiempo_navegadores(connection: Any) -> list[dict[str, Any]]:
    """Compara las estadísticas de tiempo entre todos los navegadores."""
    return _execute(
        connection,
        """
        SELECT
            navegador,
            CASE navegador
                WHEN 0 THEN 'Tienda Física'
                ELSE 'Navegador ' || navegador
            END AS nombre,
            COUNT(*) AS registros,
            ROUND(AVG(tiempo), 2) AS media,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tiempo) AS mediana,
            MIN(tiempo) AS minimo,
            MAX(tiempo) AS maximo
        FROM ventas_online
        GROUP BY navegador
        ORDER BY navegador;
        """,
    )


TOOL_DEFINITIONS = [
    {
        "name": "resumen_navegadores",
        "description": "Cantidad y porcentaje de clientes, compras y ventas totales por navegador.",
        "parameters": {},
        "handler": resumen_navegadores,
    },
    {
        "name": "estadisticas_tiempo",
        "description": "Media, mediana, moda, mínimo y máximo de tiempo, general o por navegador.",
        "parameters": {
            "navegador": {
                "type": "integer",
                "enum": [0, 1, 2, 3, 4],
                "required": False,
            }
        },
        "handler": estadisticas_tiempo,
    },
    {
        "name": "comparar_tiempo_navegadores",
        "description": "Compara registros y estadísticas de tiempo entre navegadores.",
        "parameters": {},
        "handler": comparar_tiempo_navegadores,
    },
]
