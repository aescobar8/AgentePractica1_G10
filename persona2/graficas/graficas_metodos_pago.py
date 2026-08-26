from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D


ANALISIS_DIR = Path(__file__).resolve().parents[1] / "analisis"
sys.path.insert(0, str(ANALISIS_DIR))

from analisis_metodos_pago import (  # noqa: E402
    METODOS_PAGO,
    cargar_configuracion,
    cargar_y_limpiar_datos,
)


SALIDA = Path(__file__).resolve().parent


def preparar_datos() -> pd.DataFrame:
    filas = cargar_y_limpiar_datos()
    datos = pd.DataFrame(filas, columns=["codigo", "MontoCompra"])
    datos["Método de pago"] = datos["codigo"].map(METODOS_PAGO)
    return datos


def grafica_distribucion(datos: pd.DataFrame) -> None:
    resumen = (
        datos.groupby("Método de pago", observed=True)
        .agg(Registros=("MontoCompra", "size"), Monto_total=("MontoCompra", "sum"))
        .reset_index()
        .sort_values("Registros", ascending=False)
    )
    total = int(resumen["Registros"].sum())

    colores = ["#4f86e8", "#66c2a5", "#fc8d62"]
    fig, ax = plt.subplots(figsize=(10, 7))
    sectores, _, textos_porcentaje = ax.pie(
        resumen["Registros"],
        colors=colores,
        startangle=90,
        counterclock=False,
        autopct=lambda porcentaje: f"{porcentaje:.2f}%",
        pctdistance=0.78,
        wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
    )
    for texto in textos_porcentaje:
        texto.set_fontsize(11)
        texto.set_fontweight("bold")

    etiquetas = [
        f"{metodo}: {int(registros):,} ventas/registros ({registros / total * 100:.2f}%)"
        for metodo, registros in zip(resumen["Método de pago"], resumen["Registros"])
    ]
    ax.legend(
        sectores,
        etiquetas,
        title="Método de pago — valor exacto",
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        frameon=False,
    )
    ax.text(0, 0, f"Total\n{total:,}", ha="center", va="center", fontsize=14)
    ax.set_title("Ventas por método de pago", fontsize=16, pad=18)
    ax.axis("equal")
    fig.tight_layout()
    fig.savefig(SALIDA / "distribucion_ventas_metodo_pago.png", dpi=180)
    plt.close(fig)


def grafica_comparacion_montos(datos: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    nombres = list(METODOS_PAGO.values())
    colores = ["#1b9e77", "#d95f02", "#4f6fb3"]
    monto_minimo = float(datos["MontoCompra"].min())
    monto_maximo = float(datos["MontoCompra"].max())
    margen = (monto_maximo - monto_minimo) * 0.04
    eje_x = np.linspace(max(0, monto_minimo - margen), monto_maximo + margen, 500)

    for nombre, color in zip(nombres, colores):
        valores = datos.loc[
            datos["Método de pago"] == nombre, "MontoCompra"
        ].to_numpy(dtype=float)
        desviacion = valores.std(ddof=1)
        ancho_banda = 1.06 * desviacion * len(valores) ** (-1 / 5)
        if ancho_banda <= 0:
            ancho_banda = 1.0

        diferencias = (eje_x[:, None] - valores[None, :]) / ancho_banda
        densidad = np.exp(-0.5 * diferencias**2).sum(axis=1)
        densidad /= len(valores) * ancho_banda * np.sqrt(2 * np.pi)

        media_metodo = float(valores.mean())
        ax.plot(eje_x, densidad, color=color, linewidth=2.3, label=nombre)
        ax.fill_between(eje_x, densidad, color=color, alpha=0.035)
        ax.axvline(
            media_metodo,
            color=color,
            linestyle=(0, (4, 3)),
            linewidth=1.4,
            alpha=0.9,
        )
    estadisticas = datos.groupby("Método de pago")["MontoCompra"].agg(
        ["count", "mean", "median"]
    ).reindex(nombres)

    filas_tabla = [
        [
            metodo,
            f"{int(fila['count']):,}",
            f"{fila['mean']:.3f}",
            f"{fila['median']:.3f}",
        ]
        for metodo, fila in estadisticas.iterrows()
    ]
    tabla = ax.table(
        cellText=filas_tabla,
        colLabels=["Método de pago", "Registros", "Media", "Mediana"],
        cellLoc="center",
        colLoc="center",
        colWidths=[0.38, 0.16, 0.16, 0.16],
        bbox=[0.18, -0.36, 0.64, 0.20],
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(8.5)
    for (fila, _), celda in tabla.get_celld().items():
        celda.set_edgecolor("#c8c8c8")
        celda.set_linewidth(0.7)
        if fila == 0:
            celda.set_facecolor("#e9eef5")
            celda.set_text_props(weight="bold", color="#222222")
        else:
            celda.set_facecolor("#ffffff")
    ax.set_title(
        "Distribución de los montos de compra según método de pago",
        fontsize=15,
        pad=14,
    )
    ax.set_xlabel("Monto de compra", labelpad=10)
    ax.set_ylabel("Densidad")
    asas, etiquetas = ax.get_legend_handles_labels()
    asas.append(
        Line2D(
            [0],
            [0],
            color="#555555",
            linestyle=(0, (4, 3)),
            linewidth=1.4,
        )
    )
    etiquetas.append("Media de cada método")
    ax.legend(asas, etiquetas, title="Método de pago", frameon=False)
    ax.grid(axis="both", color="#d9d9d9", linewidth=0.7, alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.89, bottom=0.31)
    fig.savefig(SALIDA / "comparacion_montos_metodo_pago.png", dpi=180)
    plt.close(fig)


def main() -> None:
    cargar_configuracion()
    datos = preparar_datos()
    grafica_distribucion(datos)
    grafica_comparacion_montos(datos)
    print(f"Gráficas guardadas en: {SALIDA}")


if __name__ == "__main__":
    main()
