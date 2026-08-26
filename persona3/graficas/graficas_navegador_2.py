from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from graficas_navegador import NAVEGADORES, conectar, cargar_configuracion


OUTPUT_DIR = Path(__file__).resolve().parent
COLORES = plt.get_cmap("Set2").colors[: len(NAVEGADORES)]


def consultar_resumen() -> list[tuple[int, int, int, Decimal]]:
    with conectar() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    navegador,
                    COUNT(*) AS total_clientes,
                    SUM(n_compras) AS total_compras,
                    SUM(venta_total) AS ventas_totales
                FROM ventas_online
                GROUP BY navegador
                ORDER BY navegador;
                """
            )
            filas = cursor.fetchall()

    if not filas:
        raise ValueError("La tabla ventas_online no contiene registros para graficar.")

    return [
        (int(navegador), int(clientes), int(compras), Decimal(ventas))
        for navegador, clientes, compras, ventas in filas
    ]


def agregar_etiquetas(
    eje: plt.Axes, barras, formato, separacion: int | float = 3
) -> None:
    etiquetas = [formato(barra.get_height()) for barra in barras]
    eje.bar_label(barras, labels=etiquetas, padding=separacion, fontsize=9)


def crear_grafica_ventas_compras(
    resumen: list[tuple[int, int, int, Decimal]],
) -> Path:
    nombres = [NAVEGADORES[fila[0]] for fila in resumen]
    compras = [fila[2] for fila in resumen]
    ventas = [float(fila[3]) for fila in resumen]

    figura, (eje_compras, eje_ventas) = plt.subplots(
        1, 2, figsize=(15, 6.5), constrained_layout=True
    )

    barras_compras = eje_compras.bar(nombres, compras, color=COLORES)
    agregar_etiquetas(eje_compras, barras_compras, lambda valor: f"{valor:,.0f}")
    eje_compras.set_title("Cantidad total de compras por navegador")
    eje_compras.set_xlabel("Navegador")
    eje_compras.set_ylabel("Número total de compras")
    eje_compras.tick_params(axis="x", rotation=20)
    eje_compras.grid(axis="y", alpha=0.25)
    eje_compras.set_ylim(0, max(compras) * 1.13)

    barras_ventas = eje_ventas.bar(nombres, ventas, color=COLORES)
    agregar_etiquetas(eje_ventas, barras_ventas, lambda valor: f"{valor:,.3f}")
    eje_ventas.set_title("Ventas totales por navegador")
    eje_ventas.set_xlabel("Navegador")
    eje_ventas.set_ylabel("Venta total")
    eje_ventas.tick_params(axis="x", rotation=20)
    eje_ventas.grid(axis="y", alpha=0.25)
    eje_ventas.set_ylim(0, max(ventas) * 1.13)

    figura.suptitle("Ventas y compras por navegador", fontsize=16)
    figura.text(
        0.5,
        -0.02,
        "Compras = SUM(n_compras) | Ventas = SUM(venta_total) | "
        "Fuente: tabla ventas_online",
        ha="center",
        fontsize=9,
    )

    ruta = OUTPUT_DIR / "ventas_compras_por_navegador.png"
    figura.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return ruta


def crear_grafica_comparacion(
    resumen: list[tuple[int, int, int, Decimal]],
) -> Path:
    nombres = [NAVEGADORES[fila[0]] for fila in resumen]
    clientes = np.array([fila[1] for fila in resumen], dtype=float)
    compras = np.array([fila[2] for fila in resumen], dtype=float)
    ventas = np.array([float(fila[3]) for fila in resumen], dtype=float)

    participaciones = {
        "Clientes/registros": clientes / clientes.sum() * 100,
        "Compras": compras / compras.sum() * 100,
        "Ventas": ventas / ventas.sum() * 100,
    }

    posiciones = np.arange(len(nombres))
    ancho = 0.24
    figura, eje = plt.subplots(figsize=(13, 8.5))

    for indice, (metrica, valores) in enumerate(participaciones.items()):
        desplazamiento = (indice - 1) * ancho
        barras = eje.bar(
            posiciones + desplazamiento,
            valores,
            width=ancho,
            label=metrica,
        )
        agregar_etiquetas(eje, barras, lambda valor: f"{valor:.1f}%", 2)

    eje.set_title("Comparación de resultados entre navegadores")
    eje.set_xlabel("Navegador")
    eje.set_ylabel("Participación sobre el total (%)")
    eje.set_xticks(posiciones, nombres)
    eje.set_ylim(0, max(valor.max() for valor in participaciones.values()) * 1.16)
    eje.grid(axis="y", alpha=0.25)
    eje.legend(title="Resultado comparado")

    tabla_datos = [
        [f"{fila[1]:,}", f"{fila[2]:,}", f"{fila[3]:,.3f}"]
        for fila in resumen
    ]
    tabla = eje.table(
        cellText=tabla_datos,
        rowLabels=nombres,
        colLabels=["Clientes/registros", "Total compras", "Ventas totales"],
        cellLoc="center",
        rowLoc="center",
        bbox=[0.08, -0.48, 0.84, 0.31],
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    figura.text(
        0.5,
        0.015,
        "La gráfica compara porcentajes; la tabla presenta los valores exactos | "
        "Fuente: tabla ventas_online",
        ha="center",
        fontsize=9,
    )
    figura.subplots_adjust(bottom=0.36)

    ruta = OUTPUT_DIR / "comparacion_resultados_navegadores.png"
    figura.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return ruta


def main() -> None:
    cargar_configuracion()
    resumen = consultar_resumen()
    grafica_ventas_compras = crear_grafica_ventas_compras(resumen)
    grafica_comparacion = crear_grafica_comparacion(resumen)

    print("Gráficas 2.0 generadas correctamente:")
    print(f"- {grafica_ventas_compras}")
    print(f"- {grafica_comparacion}")


if __name__ == "__main__":
    main()
