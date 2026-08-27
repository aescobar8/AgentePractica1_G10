from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "Id_cliente", "Edad", "Genero", "Venta_total", "N_Compras",
    "FechaCompra", "MontoCompra", "MetodoPago", "Tiempo", "Navegador",
    "Boletin", "Vale",
]
MONTH_NAMES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Analiza las ventas mensuales de Persona 1.")
    parser.add_argument("--csv", type=Path, default=root / "persona4" / "sog2_postgres_local" / "data" / "raw" / "Venta_online_c.csv")
    parser.add_argument("--output-dir", type=Path, default=root / "persona1" / "resultados")
    return parser.parse_args()


def load_and_validate(csv_path: Path) -> tuple[pd.DataFrame, dict]:
    data = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig")
    if list(data.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"Encabezado inesperado: {list(data.columns)}")
    if data.empty:
        raise ValueError("El CSV no contiene registros.")
    data["Venta_total"] = pd.to_numeric(data["Venta_total"], errors="coerce")
    data["FechaCompra"] = pd.to_datetime(data["FechaCompra"].astype("string").str.strip(), format="%d.%m.%y", errors="coerce")
    invalid = {column: int(data[column].isna().sum()) for column in ["Venta_total", "FechaCompra"] if data[column].isna().any()}
    if invalid:
        raise ValueError(f"Valores nulos o invalidos en columnas asignadas: {invalid}")
    if not data["Id_cliente"].is_unique:
        raise ValueError("Id_cliente contiene duplicados.")
    if not data["FechaCompra"].dt.year.eq(2021).all():
        raise ValueError("FechaCompra contiene fechas fuera de 2021.")
    if (data["Venta_total"] < 0).any():
        raise ValueError("Venta_total no puede contener valores negativos.")
    data["mes_num"] = data["FechaCompra"].dt.month
    data["mes"] = data["mes_num"].map(MONTH_NAMES)
    validation = {
        "archivo": str(csv_path),
        "registros": int(len(data)),
        "columnas": len(EXPECTED_COLUMNS),
        "nulos_venta_total": 0,
        "nulos_fecha_compra": 0,
        "ids_unicos": True,
        "fecha_minima": data["FechaCompra"].min().strftime("%Y-%m-%d"),
        "fecha_maxima": data["FechaCompra"].max().strftime("%Y-%m-%d"),
    }
    return data, validation


def moda(series: pd.Series) -> float:
    values = series.mode()
    return float(values.iloc[0]) if not values.empty else float("nan")


def calculate(data: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    monthly = data.groupby("mes_num").agg(
        registros=("Id_cliente", "size"),
        ventas_totales=("Venta_total", "sum"),
        venta_media=("Venta_total", "mean"),
        venta_mediana=("Venta_total", "median"),
    ).reindex(range(1, 13))
    monthly["venta_moda"] = [moda(data.loc[data["mes_num"] == month, "Venta_total"]) for month in range(1, 13)]
    monthly["mes"] = monthly.index.map(MONTH_NAMES)
    monthly = monthly.reset_index().rename(columns={"mes_num": "mes_num"})
    total_by_month = monthly.set_index("mes_num")["ventas_totales"]
    best = monthly.loc[monthly["ventas_totales"].idxmax()]
    worst = monthly.loc[monthly["ventas_totales"].idxmin()]
    summary = {
        "registros": int(len(data)),
        "ventas_totales": float(data["Venta_total"].sum()),
        "media": float(data["Venta_total"].mean()),
        "mediana": float(data["Venta_total"].median()),
        "moda": moda(data["Venta_total"]),
        "minimo": float(data["Venta_total"].min()),
        "maximo": float(data["Venta_total"].max()),
        "mes_mayores_ventas": str(best["mes"]),
        "mayores_ventas": float(best["ventas_totales"]),
        "mes_menores_ventas": str(worst["mes"]),
        "menores_ventas": float(worst["ventas_totales"]),
        "variacion_max_min_porcentaje": float((best["ventas_totales"] / worst["ventas_totales"] - 1) * 100),
        "meses_ordenados": [MONTH_NAMES[int(index)] for index in total_by_month.index],
    }
    return monthly, summary


def build_report(validation: dict, monthly: pd.DataFrame, summary: dict) -> str:
    def number(value: float) -> str:
        return f"{value:,.3f}"

    table = ["| Mes | Registros | Ventas totales | Media | Mediana | Moda |", "|---|---:|---:|---:|---:|---:|"]
    for _, row in monthly.iterrows():
        table.append(f"| {row['mes']} | {int(row['registros']):,} | {number(row['ventas_totales'])} | {number(row['venta_media'])} | {number(row['venta_mediana'])} | {number(row['venta_moda'])} |")
    return f"""# Persona 1: ventas por mes y estadisticas

## Limpieza y validacion

- Registros analizados: {validation['registros']:,}
- Columnas: {validation['columnas']}
- `Venta_total`: valores numericos, sin nulos y sin negativos.
- `FechaCompra`: fechas validas entre {validation['fecha_minima']} y {validation['fecha_maxima']}.
- `Id_cliente`: sin duplicados.

## Analisis

La venta total acumulada fue **{number(summary['ventas_totales'])}**, con media **{number(summary['media'])}**, mediana **{number(summary['mediana'])}** y moda **{number(summary['moda'])}**. El valor minimo fue **{number(summary['minimo'])}** y el maximo **{number(summary['maximo'])}**.

{chr(10).join(table)}

El mes con mayores ventas fue **{summary['mes_mayores_ventas']}**, con **{number(summary['mayores_ventas'])}**. El mes con menores ventas fue **{summary['mes_menores_ventas']}**, con **{number(summary['menores_ventas'])}**. La diferencia relativa entre ambos meses fue de **{summary['variacion_max_min_porcentaje']:.1f}%**.

## Graficas

- [Ventas totales por mes](../graficas/ventas_totales_por_mes.png)
- [Evolucion de ventas durante el ano](../graficas/evolucion_ventas_anual.png)

## Conclusion

Las ventas se distribuyeron durante los doce meses de 2021, pero no de manera uniforme. **{summary['mes_mayores_ventas']}** concentró el mayor total y **{summary['mes_menores_ventas']}** el menor. La media superior a la mediana indica que algunos registros de Venta_total altos elevan el promedio.

## Recomendaciones

1. Reforzar inventario y campañas antes de **{summary['mes_mayores_ventas']}**, tomando ese mes como referencia de demanda alta.
2. Investigar las causas de la baja observada en **{summary['mes_menores_ventas']}** y probar promociones o acciones comerciales específicas, comparando sus resultados con meses similares.

## Respuesta a la Pregunta A

La venta total mensual permite identificar la estacionalidad y priorizar recursos: se debe preparar la operación para el mes de mayor facturacion y usar el mes de menor facturacion como punto de partida para experimentar mejoras.

## Datos para reproducibilidad

Los calculos se generan desde `Venta_online_c.csv` con separador punto y coma, conservando el CSV original sin modificaciones.
"""


def main() -> None:
    args = parse_args()
    data, validation = load_and_validate(args.csv)
    monthly, summary = calculate(data)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(args.output_dir / "ventas_por_mes.csv", sep=";", index=False, encoding="utf-8-sig", float_format="%.3f")
    (args.output_dir / "metricas_persona1.json").write_text(json.dumps({"validacion": validation, "resumen": summary}, ensure_ascii=True, indent=2), encoding="utf-8")
    (args.output_dir / "analisis_persona1.md").write_text(build_report(validation, monthly, summary), encoding="utf-8")
    print(f"Resultados escritos en {args.output_dir}")


if __name__ == "__main__":
    main()
