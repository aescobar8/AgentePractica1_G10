from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import psycopg
from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[2]
PERSONA3_ENV = REPO_ROOT / "persona3" / ".env"
SHARED_ENV = REPO_ROOT / "persona4" / "sog2_postgres_local" / ".env"
OUTPUT_DIR = Path(__file__).resolve().parent

NAVEGADORES = {
    0: "Tienda Física",
    1: "Navegador 1",
    2: "Navegador 2",
    3: "Navegador 3",
    4: "Navegador 4",
}


def cargar_configuracion() -> None:
    load_dotenv(SHARED_ENV)
    load_dotenv(PERSONA3_ENV, override=True)


def conectar() -> psycopg.Connection:
    parametros = {
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }
    faltantes = [nombre for nombre, valor in parametros.items() if not valor]
    if faltantes:
        raise ValueError(
            "Faltan variables de conexión en el archivo .env: "
            + ", ".join(faltantes)
        )

    sslmode = os.getenv("POSTGRES_SSLMODE")
    if sslmode:
        parametros["sslmode"] = sslmode

    return psycopg.connect(**parametros)


def consultar_datos() -> tuple[dict[int, int], dict[int, list[float]]]:
    with conectar() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT navegador, SUM(n_compras) AS total_compras
                FROM ventas_online
                GROUP BY navegador
                ORDER BY navegador;
                """
            )
            compras = {
                int(navegador): int(total_compras)
                for navegador, total_compras in cursor.fetchall()
            }

            cursor.execute(
                """
                SELECT navegador, tiempo
                FROM ventas_online
                ORDER BY navegador, id_cliente;
                """
            )
            tiempos: dict[int, list[float]] = {
                codigo: [] for codigo in NAVEGADORES
            }
            for navegador, tiempo in cursor.fetchall():
                tiempos[int(navegador)].append(float(tiempo))

    if not compras:
        raise ValueError("La tabla ventas_online no contiene registros para graficar.")

    return compras, tiempos


def crear_grafica_circular(compras: dict[int, int]) -> Path:
    codigos = [codigo for codigo in NAVEGADORES if compras.get(codigo, 0) > 0]
    nombres = [NAVEGADORES[codigo] for codigo in codigos]
    valores = [compras[codigo] for codigo in codigos]
    colores = plt.get_cmap("Set2").colors[: len(codigos)]

    figura, eje = plt.subplots(figsize=(9, 6.5))
    sectores, _, porcentajes = eje.pie(
        valores,
        colors=colores,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.72,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    for texto in porcentajes:
        texto.set_fontsize(10)

    leyenda = [
        f"{nombre}: {valor:,} compras"
        for nombre, valor in zip(nombres, valores)
    ]
    eje.legend(
        sectores,
        leyenda,
        title="Navegadores",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )
    eje.set_title("Distribución del total de compras por navegador", pad=18)
    eje.axis("equal")
    figura.text(
        0.5,
        0.02,
        f"Total general: {sum(valores):,} compras | Fuente: tabla ventas_online",
        ha="center",
        fontsize=9,
    )

    ruta = OUTPUT_DIR / "distribucion_compras_por_navegador.png"
    figura.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return ruta


def crear_boxplot_tiempo(tiempos: dict[int, list[float]]) -> Path:
    codigos = [codigo for codigo in NAVEGADORES if tiempos.get(codigo)]
    nombres = [NAVEGADORES[codigo] for codigo in codigos]
    valores = [tiempos[codigo] for codigo in codigos]

    figura, eje = plt.subplots(figsize=(11.5, 8.5))
    cajas = eje.boxplot(
        valores,
        tick_labels=nombres,
        patch_artist=True,
        showmeans=True,
        meanprops={
            "marker": "D",
            "markerfacecolor": "black",
            "markeredgecolor": "black",
            "markersize": 5,
        },
        medianprops={"color": "black", "linewidth": 1.5},
        flierprops={
            "marker": ".",
            "markerfacecolor": "black",
            "markeredgecolor": "black",
            "markersize": 4,
        },
    )

    colores = plt.get_cmap("Set2").colors[: len(cajas["boxes"])]
    for caja, color in zip(cajas["boxes"], colores):
        caja.set_facecolor(color)

    eje.set_title("Distribución del tiempo según navegador", pad=14)
    eje.set_xlabel("Navegador")
    eje.set_ylabel("Tiempo")
    eje.grid(axis="y", alpha=0.25)

    eje.scatter([], [], marker="D", color="black", s=28, label="Media")
    eje.plot([], [], color="black", linewidth=1.5, label="Mediana")
    eje.legend(loc="upper right")

    estadisticas = []
    for grupo in valores:
        minimo, q1, mediana, q3, maximo = np.percentile(
            grupo, [0, 25, 50, 75, 100]
        )
        estadisticas.append(
            [
                f"{len(grupo):,}",
                f"{minimo:.0f}",
                f"{q1:.2f}",
                f"{mediana:.2f}",
                f"{np.mean(grupo):.2f}",
                f"{q3:.2f}",
                f"{maximo:.0f}",
            ]
        )

    tabla = eje.table(
        cellText=estadisticas,
        rowLabels=nombres,
        colLabels=["Registros", "Mín.", "Q1", "Mediana", "Media", "Q3", "Máx."],
        cellLoc="center",
        rowLoc="center",
        bbox=[0.0, -0.48, 1.0, 0.31],
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(8.5)
    figura.text(
        0.5,
        0.015,
        "Valores exactos del resumen estadístico | Fuente: tabla ventas_online",
        ha="center",
        fontsize=9,
    )
    figura.subplots_adjust(bottom=0.36)

    ruta = OUTPUT_DIR / "boxplot_tiempo_por_navegador.png"
    figura.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return ruta


def main() -> None:
    cargar_configuracion()
    compras, tiempos = consultar_datos()
    grafica_circular = crear_grafica_circular(compras)
    grafica_boxplot = crear_boxplot_tiempo(tiempos)

    print("Gráficas generadas correctamente:")
    print(f"- {grafica_circular}")
    print(f"- {grafica_boxplot}")


if __name__ == "__main__":
    main()
