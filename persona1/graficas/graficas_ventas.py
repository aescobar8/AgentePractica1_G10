from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Genera las graficas de Persona 1.")
    parser.add_argument("--input", type=Path, default=root / "persona1" / "resultados" / "ventas_por_mes.csv")
    parser.add_argument("--output-dir", type=Path, default=root / "persona1" / "graficas")
    return parser.parse_args()


def annotate(axis, bars: object, values: pd.Series) -> None:
    for bar, value in zip(bars, values):
        axis.annotate(f"{value:,.0f}", (bar.get_x() + bar.get_width() / 2, bar.get_height()), xytext=(0, 5), textcoords="offset points", ha="center", fontsize=8)


def main() -> None:
    args = parse_args()
    monthly = pd.read_csv(args.input, sep=";", encoding="utf-8-sig")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titlesize": 15, "axes.labelsize": 11})

    figure, axis = plt.subplots(figsize=(13, 7))
    bars = axis.bar(monthly["mes"], monthly["ventas_totales"], color="#0f766e")
    annotate(axis, bars, monthly["ventas_totales"])
    axis.set_title("Ventas totales por mes - 2021")
    axis.set_xlabel("Mes de compra")
    axis.set_ylabel("Venta total acumulada")
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(args.output_dir / "ventas_totales_por_mes.png", dpi=220, bbox_inches="tight")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(13, 7))
    axis.plot(monthly["mes"], monthly["ventas_totales"], marker="o", linewidth=2.5, color="#c2410c")
    for _, row in monthly.iterrows():
        axis.annotate(f"{row['ventas_totales']:,.0f}", (row["mes"], row["ventas_totales"]), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)
    axis.set_title("Evolucion de las ventas durante el ano - 2021")
    axis.set_xlabel("Mes de compra")
    axis.set_ylabel("Venta total acumulada")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(args.output_dir / "evolucion_ventas_anual.png", dpi=220, bbox_inches="tight")
    plt.close(figure)
    print(f"Graficas escritas en {args.output_dir}")


if __name__ == "__main__":
    main()
