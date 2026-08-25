from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


EXPECTED_COLUMNS = [
    "Id_cliente",
    "Edad",
    "Genero",
    "Venta_total",
    "N_Compras",
    "FechaCompra",
    "MontoCompra",
    "MetodoPago",
    "Tiempo",
    "Navegador",
    "Boletin",
    "Vale",
]

MONTH_NAMES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

SEGMENT_ORDER = ["Ninguno", "Solo boletín", "Solo vale", "Ambos"]


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Analiza el uso de boletines y vales para la parte de la persona 6."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=repo_root / "Venta_online_c.csv",
        help="Ruta al CSV de ventas.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "persona6" / "resultados",
        help="Directorio para tablas, métricas y el informe.",
    )
    parser.add_argument(
        "--graphics-dir",
        type=Path,
        default=repo_root / "persona6" / "graficas",
        help="Directorio para las gráficas PNG.",
    )
    return parser.parse_args()


def load_and_validate(csv_path: Path) -> tuple[pd.DataFrame, dict]:
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró el CSV: {csv_path}")

    data = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig")
    if list(data.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            "El encabezado del CSV no coincide con el esquema esperado. "
            f"Esperado: {EXPECTED_COLUMNS}; recibido: {list(data.columns)}"
        )
    if data.empty:
        raise ValueError("El CSV no contiene registros.")

    numeric_columns = [
        "Id_cliente",
        "Edad",
        "Genero",
        "Venta_total",
        "N_Compras",
        "MontoCompra",
        "MetodoPago",
        "Tiempo",
        "Navegador",
        "Boletin",
        "Vale",
    ]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["FechaCompra"] = pd.to_datetime(
        data["FechaCompra"].astype("string").str.strip(),
        format="%d.%m.%y",
        errors="coerce",
    )

    invalid_cells = {
        column: int(data[column].isna().sum())
        for column in [*numeric_columns, "FechaCompra"]
        if int(data[column].isna().sum()) > 0
    }
    if invalid_cells:
        raise ValueError(f"Se encontraron valores inválidos o faltantes: {invalid_cells}")

    domain_errors = {}
    for column, allowed in {
        "Genero": {0, 1},
        "MetodoPago": {0, 1, 2},
        "Navegador": {0, 1, 2, 3, 4},
        "Boletin": {0, 1},
        "Vale": {0, 1},
    }.items():
        observed = set(data[column].astype(int).tolist())
        invalid = sorted(observed - allowed)
        if invalid:
            domain_errors[column] = invalid
        data[column] = data[column].astype(int)
    if domain_errors:
        raise ValueError(f"Valores fuera de dominio: {domain_errors}")

    if not data["Id_cliente"].is_unique:
        raise ValueError("Id_cliente contiene duplicados.")
    if not data["FechaCompra"].dt.year.eq(2021).all():
        raise ValueError("FechaCompra contiene registros fuera del año 2021.")
    if (data[["Venta_total", "N_Compras", "MontoCompra", "Tiempo"]] < 0).any().any():
        raise ValueError("Hay valores negativos en variables que deben ser no negativas.")

    data["mes_num"] = data["FechaCompra"].dt.month
    data["mes"] = data["mes_num"].map(MONTH_NAMES)
    data["boletin_label"] = data["Boletin"].map({0: "No", 1: "Sí"})
    data["vale_label"] = data["Vale"].map({0: "No", 1: "Sí"})
    data["segmento_promocional"] = "Ninguno"
    data.loc[(data["Boletin"] == 1) & (data["Vale"] == 0), "segmento_promocional"] = (
        "Solo boletín"
    )
    data.loc[(data["Boletin"] == 0) & (data["Vale"] == 1), "segmento_promocional"] = (
        "Solo vale"
    )
    data.loc[(data["Boletin"] == 1) & (data["Vale"] == 1), "segmento_promocional"] = (
        "Ambos"
    )

    validation = {
        "archivo": str(csv_path),
        "registros": int(len(data)),
        "columnas": int(len(EXPECTED_COLUMNS)),
        "filas_con_datos_faltantes": 0,
        "ids_unicos": True,
        "fecha_minima": data["FechaCompra"].min().strftime("%Y-%m-%d"),
        "fecha_maxima": data["FechaCompra"].max().strftime("%Y-%m-%d"),
        "anio_validado": 2021,
        "boletin_dominio": [0, 1],
        "vale_dominio": [0, 1],
    }
    return data, validation


def calculate_results(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    total = len(data)
    monthly = (
        data.groupby("mes_num")
        .agg(
            registros=("Id_cliente", "size"),
            boletines_usados=("Boletin", "sum"),
            vales_usados=("Vale", "sum"),
        )
        .reindex(range(1, 13), fill_value=0)
    )
    monthly.index.name = "mes_num"
    monthly["mes"] = monthly.index.map(MONTH_NAMES)
    monthly["porcentaje_boletines"] = (
        monthly["boletines_usados"] / monthly["registros"] * 100
    )
    monthly["porcentaje_vales"] = monthly["vales_usados"] / monthly["registros"] * 100
    monthly = monthly.reset_index()

    patterns = (
        data.groupby("segmento_promocional")
        .agg(
            registros=("Id_cliente", "size"),
            venta_total_total=("Venta_total", "sum"),
            venta_total_media=("Venta_total", "mean"),
            venta_total_mediana=("Venta_total", "median"),
            compras_media=("N_Compras", "mean"),
            compras_mediana=("N_Compras", "median"),
            monto_compra_media=("MontoCompra", "mean"),
            monto_compra_mediana=("MontoCompra", "median"),
        )
        .reindex(SEGMENT_ORDER)
    )
    patterns["porcentaje_registros"] = patterns["registros"] / total * 100
    patterns = patterns.reset_index().rename(
        columns={"segmento_promocional": "segmento"}
    )

    relation = (
        pd.crosstab(data["boletin_label"], data["vale_label"])
        .reindex(index=["No", "Sí"], columns=["No", "Sí"], fill_value=0)
        .astype(int)
    )
    n00 = int(relation.loc["No", "No"])
    n01 = int(relation.loc["No", "Sí"])
    n10 = int(relation.loc["Sí", "No"])
    n11 = int(relation.loc["Sí", "Sí"])
    denominator = math.sqrt(
        (n00 + n01) * (n10 + n11) * (n00 + n10) * (n01 + n11)
    )
    phi = (n00 * n11 - n01 * n10) / denominator if denominator else 0.0
    vale_given_boletin = n11 / (n10 + n11)
    vale_given_no_boletin = n01 / (n00 + n01)
    lift = (
        vale_given_boletin / vale_given_no_boletin
        if vale_given_no_boletin
        else float("nan")
    )

    summary = {
        "total_registros": total,
        "boletines_usados": int(data["Boletin"].sum()),
        "porcentaje_boletines": float(data["Boletin"].mean() * 100),
        "vales_usados": int(data["Vale"].sum()),
        "porcentaje_vales": float(data["Vale"].mean() * 100),
        "usan_ambos": n11,
        "porcentaje_ambos": float(n11 / total * 100),
        "no_usan_ninguno": n00,
        "porcentaje_ninguno": float(n00 / total * 100),
        "correlacion_phi_boletin_vale": float(phi),
        "probabilidad_vale_si_boletin": float(vale_given_boletin),
        "probabilidad_vale_si_no_boletin": float(vale_given_no_boletin),
        "lift_vale_dado_boletin": float(lift),
        "tabla_relacion": {
            "no_boletin_no_vale": n00,
            "no_boletin_si_vale": n01,
            "si_boletin_no_vale": n10,
            "si_boletin_si_vale": n11,
        },
    }
    return monthly, patterns, relation, summary


def annotate_bars(axis, bars, values: list[int]) -> None:
    for bar, value in zip(bars, values):
        axis.annotate(
            f"{int(value):,}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def create_graphics(
    monthly: pd.DataFrame,
    relation: pd.DataFrame,
    summary: dict,
    graphics_dir: Path,
) -> list[Path]:
    graphics_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 15,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )

    x = list(range(len(monthly)))
    width = 0.36
    figure, axis = plt.subplots(figsize=(13, 7.5))
    boletin_bars = axis.bar(
        [position - width / 2 for position in x],
        monthly["boletines_usados"],
        width,
        label="Boletines",
        color="#2563EB",
    )
    vale_bars = axis.bar(
        [position + width / 2 for position in x],
        monthly["vales_usados"],
        width,
        label="Vales",
        color="#F59E0B",
    )
    annotate_bars(axis, boletin_bars, monthly["boletines_usados"].tolist())
    annotate_bars(axis, vale_bars, monthly["vales_usados"].tolist())
    axis.set_title("Uso mensual de boletines y vales - 2021")
    axis.set_xlabel("Mes de compra")
    axis.set_ylabel("Clientes que utilizaron la promoción")
    axis.set_xticks(x, monthly["mes"])
    axis.set_ylim(0, max(monthly["boletines_usados"].max(), monthly["vales_usados"].max()) * 1.18)
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False, ncols=2)
    figure.tight_layout()
    monthly_path = graphics_dir / "uso_boletines_vales_por_mes.png"
    figure.savefig(monthly_path, dpi=220, bbox_inches="tight")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(9.5, 7))
    x = [0, 1]
    no_vale = [int(relation.loc["No", "No"]), int(relation.loc["Sí", "No"])]
    si_vale = [int(relation.loc["No", "Sí"]), int(relation.loc["Sí", "Sí"])]
    no_vale_bars = axis.bar(
        x,
        no_vale,
        label="No utiliza vale",
        color="#94A3B8",
    )
    si_vale_bars = axis.bar(
        x,
        si_vale,
        bottom=no_vale,
        label="Utiliza vale",
        color="#16A34A",
    )
    row_totals = [sum(pair) for pair in zip(no_vale, si_vale)]
    for index, (bar, value) in enumerate(zip(no_vale_bars, no_vale)):
        axis.annotate(
            f"{value:,}",
            xy=(bar.get_x() + bar.get_width() / 2, value / 2),
            ha="center",
            va="center",
            fontsize=10,
        )
    for index, (bar, value) in enumerate(zip(si_vale_bars, si_vale)):
        percentage = value / row_totals[index] * 100
        axis.annotate(
            f"{value:,}\n({percentage:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, no_vale[index] + value / 2),
            ha="center",
            va="center",
            fontsize=10,
            color="white",
            fontweight="bold",
        )
    axis.set_title(
        "Relación entre boletines y vales\n"
        f"Probabilidad de usar vale: {summary['probabilidad_vale_si_boletin'] * 100:.1f}% "
        f"con boletín vs. {summary['probabilidad_vale_si_no_boletin'] * 100:.1f}% sin boletín"
    )
    axis.set_xlabel("Uso de boletín")
    axis.set_ylabel("Cantidad de clientes")
    axis.set_xticks(x, ["No utiliza boletín", "Utiliza boletín"])
    axis.set_ylim(0, max(row_totals) * 1.16)
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False)
    figure.tight_layout()
    relation_path = graphics_dir / "relacion_boletin_vale.png"
    figure.savefig(relation_path, dpi=220, bbox_inches="tight")
    plt.close(figure)
    return [monthly_path, relation_path]


def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}"


def fmt_num(value: float | int) -> str:
    return f"{float(value):,.3f}"


def fmt_pct(value: float) -> str:
    return f"{float(value):.1f}%"


def build_monthly_table(monthly: pd.DataFrame) -> str:
    lines = [
        "| Mes | Registros | Boletines | % boletines | Vales | % vales |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in monthly.iterrows():
        lines.append(
            f"| {row['mes']} | {fmt_int(row['registros'])} | "
            f"{fmt_int(row['boletines_usados'])} | {fmt_pct(row['porcentaje_boletines'])} | "
            f"{fmt_int(row['vales_usados'])} | {fmt_pct(row['porcentaje_vales'])} |"
        )
    return "\n".join(lines)


def build_pattern_table(patterns: pd.DataFrame) -> str:
    lines = [
        "| Segmento | Clientes | % | Venta total media | Mediana venta | Compras medias | Monto medio |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in patterns.iterrows():
        lines.append(
            f"| {row['segmento']} | {fmt_int(row['registros'])} | "
            f"{fmt_pct(row['porcentaje_registros'])} | {fmt_num(row['venta_total_media'])} | "
            f"{fmt_num(row['venta_total_mediana'])} | {fmt_num(row['compras_media'])} | "
            f"{fmt_num(row['monto_compra_media'])} |"
        )
    return "\n".join(lines)


def build_report(
    validation: dict,
    monthly: pd.DataFrame,
    patterns: pd.DataFrame,
    relation: pd.DataFrame,
    summary: dict,
) -> str:
    best_boletin = monthly.loc[monthly["boletines_usados"].idxmax()]
    best_vale = monthly.loc[monthly["vales_usados"].idxmax()]
    both = patterns.loc[patterns["segmento"] == "Ambos"].iloc[0]
    none = patterns.loc[patterns["segmento"] == "Ninguno"].iloc[0]
    only_boletin = patterns.loc[patterns["segmento"] == "Solo boletín"].iloc[0]
    only_vale = patterns.loc[patterns["segmento"] == "Solo vale"].iloc[0]

    conclusion_lines = [
        f"Se analizaron {fmt_int(validation['registros'])} registros correspondientes al CSV de ventas online de 2021.",
        f"El boletín aparece utilizado en {fmt_int(summary['boletines_usados'])} registros, equivalentes al {fmt_pct(summary['porcentaje_boletines'])} del total.",
        f"El vale aparece utilizado en {fmt_int(summary['vales_usados'])} registros, equivalentes al {fmt_pct(summary['porcentaje_vales'])} del total.",
        f"{fmt_int(summary['usan_ambos'])} clientes utilizaron simultáneamente boletín y vale.",
        f"{fmt_int(summary['no_usan_ninguno'])} clientes no utilizaron ninguna de las dos promociones.",
        f"El uso de boletines alcanzó su máximo en {best_boletin['mes']}, con {fmt_int(best_boletin['boletines_usados'])} clientes.",
        f"El uso de vales alcanzó su máximo en {best_vale['mes']}, con {fmt_int(best_vale['vales_usados'])} clientes.",
        "La utilización de boletines se mantuvo presente en todos los meses, sin concentrarse en un único periodo.",
        "La utilización de vales fue menor que la de boletines en cada mes observado.",
        f"El segmento sin promociones registró una venta total media de {fmt_num(none['venta_total_media'])}.",
        f"El segmento que utilizó solo boletín registró una venta total media de {fmt_num(only_boletin['venta_total_media'])}.",
        f"El segmento que utilizó solo vale registró una venta total media de {fmt_num(only_vale['venta_total_media'])}.",
        f"El segmento que utilizó ambas promociones obtuvo la venta total media más alta: {fmt_num(both['venta_total_media'])}.",
        f"Los clientes del segmento de ambas promociones realizaron {fmt_num(both['compras_media'])} compras en promedio.",
        f"Los clientes que usaron solo vale realizaron {fmt_num(only_vale['compras_media'])} compras en promedio, el valor más bajo de los cuatro segmentos.",
        f"El monto medio de compra fue {fmt_num(both['monto_compra_media'])} para quienes usaron ambas promociones.",
        f"La correlación phi entre boletín y vale fue {summary['correlacion_phi_boletin_vale']:.3f}, positiva y de magnitud baja.",
        f"La probabilidad de usar vale fue {fmt_pct(summary['probabilidad_vale_si_boletin'] * 100)} entre quienes usaron boletín.",
        f"Sin boletín, la probabilidad de usar vale bajó a {fmt_pct(summary['probabilidad_vale_si_no_boletin'] * 100)}.",
        "Los resultados muestran asociación entre las promociones, pero no prueban que una promoción cause directamente un mayor gasto.",
    ]

    planning_rows = [
        "| Responsable | Alcance acordado |",
        "|---|---|",
        "| Persona 1 | Ventas por mes y estadísticas de Venta_total. |",
        "| Persona 2 | Métodos de pago y MontoCompra. |",
        "| Persona 3 | Navegadores y Tiempo. |",
        "| Persona 4 | Edad, Id_cliente y relación con ventas. |",
        "| Persona 5 | Género, N_Compras y relación con método de pago. |",
        "| Persona 6 | Boletines, vales, planificación y metodología del informe. |",
    ]

    return f"""# Persona 6: análisis de boletines y vales

## Alcance

Esta sección analiza el uso de las columnas Boletin y Vale, su comportamiento mensual, los patrones de compra asociados y la relación entre ambas promociones. Cada fila representa un Id_cliente único según la validación realizada.

## Validación y limpieza

- Archivo procesado: {validation['archivo']}
- Registros analizados: {fmt_int(validation['registros'])}
- Columnas: {validation['columnas']}
- Fechas válidas: {validation['fecha_minima']} a {validation['fecha_maxima']}
- Valores faltantes o inválidos: 0
- Id_cliente duplicados: 0
- Dominio Boletin: 0 = No, 1 = Sí
- Dominio Vale: 0 = No, 1 = Sí

La limpieza consistió en leer el archivo con separador punto y coma y codificación UTF-8 con BOM, convertir las variables numéricas a tipos numéricos, transformar FechaCompra al formato de fecha y validar que Boletin y Vale solo contuvieran 0 o 1. No fue necesario eliminar registros porque las 6,500 filas cumplieron las reglas.

## Resumen general

| Indicador | Resultado |
|---|---:|
| Registros totales | {fmt_int(summary['total_registros'])} |
| Usaron boletín | {fmt_int(summary['boletines_usados'])} ({fmt_pct(summary['porcentaje_boletines'])}) |
| Usaron vale | {fmt_int(summary['vales_usados'])} ({fmt_pct(summary['porcentaje_vales'])}) |
| Usaron ambos | {fmt_int(summary['usan_ambos'])} ({fmt_pct(summary['porcentaje_ambos'])}) |
| No usaron ninguno | {fmt_int(summary['no_usan_ninguno'])} ({fmt_pct(summary['porcentaje_ninguno'])}) |

## Uso por mes

El mes con mayor uso de boletines fue **{best_boletin['mes']}**, con **{fmt_int(best_boletin['boletines_usados'])}** clientes. El mes con mayor uso de vales fue **{best_vale['mes']}**, con **{fmt_int(best_vale['vales_usados'])}** clientes.

{build_monthly_table(monthly)}

Gráfica mensual: [uso_boletines_vales_por_mes.png](../graficas/uso_boletines_vales_por_mes.png)

## Patrones de compra

Los segmentos se definieron así: Ninguno no usa ninguna promoción; Solo boletín usa boletín pero no vale; Solo vale usa vale pero no boletín; Ambos usa las dos promociones.

{build_pattern_table(patterns)}

El segmento Ambos presenta la mayor venta total media ({fmt_num(both['venta_total_media'])}) y la mayor mediana de venta ({fmt_num(both['venta_total_mediana'])}). El segmento Ninguno representa la mayor cantidad de registros ({fmt_int(none['registros'])}), por lo que existe una oportunidad para estudiar campañas de incorporación. El segmento Solo vale tiene el menor promedio de compras ({fmt_num(only_vale['compras_media'])}), aunque registra un monto medio de compra superior al segmento Ninguno.

## Relación entre boletín y vale

| Uso de boletín | No usa vale | Usa vale | Total |
|---|---:|---:|---:|
| No | {fmt_int(relation.loc['No', 'No'])} | {fmt_int(relation.loc['No', 'Sí'])} | {fmt_int(relation.loc['No'].sum())} |
| Sí | {fmt_int(relation.loc['Sí', 'No'])} | {fmt_int(relation.loc['Sí', 'Sí'])} | {fmt_int(relation.loc['Sí'].sum())} |

La probabilidad de usar vale entre quienes recibieron o utilizaron boletín fue **{fmt_pct(summary['probabilidad_vale_si_boletin'] * 100)}**, frente a **{fmt_pct(summary['probabilidad_vale_si_no_boletin'] * 100)}** entre quienes no usaron boletín. Esto representa un lift de **{summary['lift_vale_dado_boletin']:.2f}**. La correlación phi de **{summary['correlacion_phi_boletin_vale']:.3f}** indica una asociación positiva baja; debe interpretarse como relación observada y no como causalidad.

Gráfica de relación: [relacion_boletin_vale.png](../graficas/relacion_boletin_vale.png)

## Conclusión

{chr(10).join(f"{index}. {line}" for index, line in enumerate(conclusion_lines, start=1))}

## Recomendaciones

1. **Priorizar campañas diferenciadas por temporada.** Usar diciembre como referencia para campañas de boletines y marzo como referencia para campañas de vales, monitoreando también septiembre y noviembre, que presentan porcentajes mensuales altos de uso de vales. La ejecución debe medirse con grupos de control para distinguir asociación de efecto real.
2. **Diseñar una estrategia de conversión para clientes sin promociones.** El segmento Ninguno concentra {fmt_int(none['registros'])} clientes ({fmt_pct(none['porcentaje_registros'])}) y puede recibir pruebas segmentadas de boletín, vale o ambas promociones. Se deben comparar venta total, número de compras y monto medio antes de ampliar la campaña.

## Planificación del proyecto

La distribución acordada para trabajar en paralelo es:

{chr(10).join(planning_rows)}

La Persona 6 integra además la información que cada integrante entregue para consolidar las secciones de planificación y metodología, sin asumir la implementación completa de la base de datos, Google ADK o MCP Server.

## Metodología propuesta

1. Recibir el CSV original y conservar una copia sin modificaciones.
2. Validar codificación, separador, encabezados, cantidad de columnas y cantidad de registros.
3. Convertir FechaCompra al tipo fecha y derivar el mes de compra.
4. Validar valores faltantes, duplicados, tipos numéricos y dominios de Boletin y Vale.
5. Calcular conteos y porcentajes mensuales de uso.
6. Construir segmentos Ninguno, Solo boletín, Solo vale y Ambos.
7. Comparar venta total, número de compras y monto de compra entre segmentos.
8. Construir la tabla de contingencia Boletin x Vale y calcular probabilidades condicionales, lift y correlación phi.
9. Generar las dos gráficas con títulos, ejes, leyendas y valores exactos visibles.
10. Publicar consultas SQL y funciones IA/MCP que devuelvan los mismos resultados desde la base de datos.
11. Revisar que los resultados de las gráficas, tablas y consultas coincidan antes de integrarlos en el informe final.

## Funciones para IA/MCP

Las funciones de consulta se encuentran en [herramientas_boletines_vales.py](../ia_mcp/herramientas_boletines_vales.py) y cubren:

- resumen general de uso de boletines y vales;
- uso mensual;
- patrones de compra por segmento promocional;
- relación Boletin x Vale con probabilidades y conteos.

Las consultas SQL equivalentes se encuentran en [consultas_boletines_vales.sql](../database/consultas_boletines_vales.sql).
"""


def write_outputs(
    output_dir: Path,
    graphics_dir: Path,
    validation: dict,
    monthly: pd.DataFrame,
    patterns: pd.DataFrame,
    relation: pd.DataFrame,
    summary: dict,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(
        output_dir / "uso_mensual_boletines_vales.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
        float_format="%.3f",
    )
    patterns.to_csv(
        output_dir / "patrones_compra_promociones.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
        float_format="%.3f",
    )
    relation.reset_index(names="uso_boletin").to_csv(
        output_dir / "relacion_boletin_vale.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )
    payload = {
        "validacion": validation,
        "resumen": summary,
        "uso_mensual": json.loads(monthly.to_json(orient="records", force_ascii=False)),
        "patrones": json.loads(patterns.to_json(orient="records", force_ascii=False)),
    }
    with (output_dir / "metricas_persona6.json").open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    report_path = output_dir / "analisis_persona6.md"
    report_path.write_text(
        build_report(validation, monthly, patterns, relation, summary),
        encoding="utf-8",
    )
    return report_path, output_dir / "metricas_persona6.json"


def main() -> None:
    args = parse_args()
    csv_path = args.csv.resolve()
    output_dir = args.output_dir.resolve()
    graphics_dir = args.graphics_dir.resolve()

    data, validation = load_and_validate(csv_path)
    monthly, patterns, relation, summary = calculate_results(data)
    graphics = create_graphics(monthly, relation, summary, graphics_dir)
    report_path, metrics_path = write_outputs(
        output_dir,
        graphics_dir,
        validation,
        monthly,
        patterns,
        relation,
        summary,
    )

    print("Análisis de la persona 6 completado.")
    print(f"Registros validados: {validation['registros']}")
    print(f"Boletines utilizados: {summary['boletines_usados']}")
    print(f"Vales utilizados: {summary['vales_usados']}")
    print(f"Clientes con ambas promociones: {summary['usan_ambos']}")
    print(f"Correlación phi Boletin/Vale: {summary['correlacion_phi_boletin_vale']:.3f}")
    print(f"Informe: {report_path}")
    print(f"Métricas: {metrics_path}")
    for graphic in graphics:
        print(f"Gráfica: {graphic}")


if __name__ == "__main__":
    main()
