from __future__ import annotations

from decimal import Decimal
from typing import Any


def _json_safe(value: Any) -> Any:
    """Convierte valores de PostgreSQL a tipos compatibles con JSON."""
    if isinstance(value, Decimal):
        return float(value)
    return value


def _execute(
    connection: Any, query: str, params: tuple[Any, ...] = ()
) -> list[dict[str, Any]]:
    """Ejecuta una consulta y retorna sus filas como diccionarios."""
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        return [
            {column: _json_safe(value) for column, value in zip(columns, row)}
            for row in cursor.fetchall()
        ]


def persona4_estadisticas_edad(connection: Any) -> list[dict[str, Any]]:
    """Calcula estadísticas descriptivas de la edad de los clientes."""
    return _execute(
        connection,
        """
        SELECT
            COUNT(*) AS clientes,
            ROUND(AVG(edad), 2) AS media,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY edad) AS mediana,
            MODE() WITHIN GROUP (ORDER BY edad) AS moda,
            MIN(edad) AS minimo,
            MAX(edad) AS maximo
        FROM ventas_online;
        """,
    )


def persona4_resumen_grupos_edad(connection: Any) -> list[dict[str, Any]]:
    """Compara clientes, ventas y comportamiento de compra entre grupos de edad."""
    return _execute(
        connection,
        """
        WITH clientes_segmentados AS (
            SELECT
                id_cliente,
                edad,
                venta_total,
                n_compras,
                monto_compra,
                CASE
                    WHEN edad BETWEEN 18 AND 24 THEN '18-24'
                    WHEN edad BETWEEN 25 AND 34 THEN '25-34'
                    WHEN edad BETWEEN 35 AND 44 THEN '35-44'
                    WHEN edad BETWEEN 45 AND 54 THEN '45-54'
                    WHEN edad BETWEEN 55 AND 64 THEN '55-64'
                    WHEN edad >= 65 THEN '65+'
                END AS grupo_edad,
                CASE
                    WHEN edad BETWEEN 18 AND 24 THEN 1
                    WHEN edad BETWEEN 25 AND 34 THEN 2
                    WHEN edad BETWEEN 35 AND 44 THEN 3
                    WHEN edad BETWEEN 45 AND 54 THEN 4
                    WHEN edad BETWEEN 55 AND 64 THEN 5
                    WHEN edad >= 65 THEN 6
                END AS orden_grupo
            FROM ventas_online
        )
        SELECT
            grupo_edad,
            COUNT(DISTINCT id_cliente) AS clientes,
            ROUND(
                100.0 * COUNT(DISTINCT id_cliente)
                / SUM(COUNT(DISTINCT id_cliente)) OVER (),
                2
            ) AS porcentaje_clientes,
            ROUND(SUM(venta_total), 2) AS venta_total,
            ROUND(AVG(venta_total), 2) AS venta_promedio,
            SUM(n_compras) AS compras_totales,
            ROUND(AVG(n_compras), 2) AS compras_promedio,
            ROUND(AVG(monto_compra), 2) AS monto_compra_promedio
        FROM clientes_segmentados
        WHERE grupo_edad IS NOT NULL
        GROUP BY grupo_edad, orden_grupo
        ORDER BY orden_grupo;
        """,
    )


def persona4_extremos_grupos_edad(connection: Any) -> list[dict[str, Any]]:
    """Identifica grupos extremos según ventas y frecuencia de compra."""
    return _execute(
        connection,
        """
        WITH resumen AS (
            SELECT
                CASE
                    WHEN edad BETWEEN 18 AND 24 THEN '18-24'
                    WHEN edad BETWEEN 25 AND 34 THEN '25-34'
                    WHEN edad BETWEEN 35 AND 44 THEN '35-44'
                    WHEN edad BETWEEN 45 AND 54 THEN '45-54'
                    WHEN edad BETWEEN 55 AND 64 THEN '55-64'
                    WHEN edad >= 65 THEN '65+'
                END AS grupo_edad,
                SUM(venta_total) AS venta_total,
                AVG(venta_total) AS venta_promedio,
                AVG(n_compras) AS compras_promedio
            FROM ventas_online
            GROUP BY grupo_edad
        )
        SELECT
            (SELECT grupo_edad
             FROM resumen
             WHERE grupo_edad IS NOT NULL
             ORDER BY venta_total DESC
             LIMIT 1) AS mayor_venta_total,

            (SELECT grupo_edad
             FROM resumen
             WHERE grupo_edad IS NOT NULL
             ORDER BY venta_total ASC
             LIMIT 1) AS menor_venta_total,

            (SELECT grupo_edad
             FROM resumen
             WHERE grupo_edad IS NOT NULL
             ORDER BY venta_promedio DESC
             LIMIT 1) AS mayor_venta_promedio,

            (SELECT grupo_edad
             FROM resumen
             WHERE grupo_edad IS NOT NULL
             ORDER BY venta_promedio ASC
             LIMIT 1) AS menor_venta_promedio,

            (SELECT grupo_edad
             FROM resumen
             WHERE grupo_edad IS NOT NULL
             ORDER BY compras_promedio DESC
             LIMIT 1) AS mayor_compras_promedio,

            (SELECT grupo_edad
             FROM resumen
             WHERE grupo_edad IS NOT NULL
             ORDER BY compras_promedio ASC
             LIMIT 1) AS menor_compras_promedio;
        """,
    )


def persona4_correlacion_edad_ventas(connection: Any) -> dict[str, Any]:
    """Calcula e interpreta la correlación lineal de Pearson entre Edad y Venta_total."""
    rows = _execute(
        connection,
        """
        SELECT
            CORR(edad, venta_total) AS coeficiente_pearson
        FROM ventas_online;
        """,
    )

    coeficiente = rows[0]["coeficiente_pearson"]

    if coeficiente is None:
        interpretacion = (
            "No fue posible calcular la correlación entre edad y venta total."
        )
    else:
        valor = abs(float(coeficiente))

        if valor < 0.10:
            intensidad = "prácticamente nula"
        elif valor < 0.30:
            intensidad = "débil"
        elif valor < 0.50:
            intensidad = "moderada"
        else:
            intensidad = "fuerte"

        if float(coeficiente) > 0:
            direccion = "positiva"
        elif float(coeficiente) < 0:
            direccion = "negativa"
        else:
            direccion = "sin dirección"

        interpretacion = (
            f"La relación lineal entre edad y venta total es {intensidad} "
            f"y {direccion}. La edad por sí sola no debe interpretarse como "
            f"un predictor relevante de las ventas cuando el coeficiente "
            f"está cercano a cero."
        )

    return {
        "coeficiente_pearson": coeficiente,
        "interpretacion": interpretacion,
    }


TOOL_DEFINITIONS = [
    {
        "name": "persona4_estadisticas_edad",
        "description": (
            "Calcula media, mediana, moda, edad mínima, edad máxima y cantidad "
            "de clientes. Úsala para preguntas sobre estadísticas generales "
            "de edad."
        ),
        "parameters": {},
        "handler": persona4_estadisticas_edad,
    },
    {
        "name": "persona4_resumen_grupos_edad",
        "description": (
            "Compara clientes, ventas, frecuencia de compras y monto promedio "
            "entre los grupos de edad 18-24, 25-34, 35-44, 45-54, 55-64 y 65+. "
            "Úsala para analizar patrones de compra o comparar segmentos por edad."
        ),
        "parameters": {},
        "handler": persona4_resumen_grupos_edad,
    },
    {
        "name": "persona4_extremos_grupos_edad",
        "description": (
            "Identifica los grupos de edad con mayor y menor venta total, "
            "venta promedio y promedio de compras. Úsala para preguntas sobre "
            "qué segmento compra o vende más o menos según una métrica concreta."
        ),
        "parameters": {},
        "handler": persona4_extremos_grupos_edad,
    },
    {
        "name": "persona4_correlacion_edad_ventas",
        "description": (
            "Calcula e interpreta la correlación lineal de Pearson entre la edad "
            "del cliente y la venta total. Úsala para preguntas sobre la relación "
            "entre edad y ventas."
        ),
        "parameters": {},
        "handler": persona4_correlacion_edad_ventas,
    },
]
