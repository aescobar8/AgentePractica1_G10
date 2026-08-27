from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from statistics import mean, median, multimode

import psycopg
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
conexion_env = REPO_ROOT / "persona3" / ".env"
  

# Navegadores dis 
NAVEGADORES = {
    0: "Tienda Física",
    1: "Navegador 1",
    2: "Navegador 2",
    3: "Navegador 3",
    4: "Navegador 4",
}


# 
def cargar_configuracion() -> None:    
    load_dotenv(conexion_env, override=True)


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


def cargar_datos() -> tuple[list[tuple[int, int, int, Decimal]], list[float]]:
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
            resumen = cursor.fetchall()

            cursor.execute("SELECT tiempo FROM ventas_online ORDER BY id_cliente;")
            tiempos = [float(fila[0]) for fila in cursor.fetchall()]

    if not resumen or not tiempos:
        raise ValueError("La tabla ventas_online no contiene registros para analizar.")

    datos_resumen = [
        (int(fila[0]), int(fila[1]), int(fila[2]), Decimal(fila[3]))
        for fila in resumen
    ]
    return datos_resumen, tiempos


def mostrar_resultados(
    resumen: list[tuple[int, int, int, Decimal]], tiempos: list[float]
) -> None:
    metricas = {
        codigo: (clientes, compras, ventas)
        for codigo, clientes, compras, ventas in resumen
    }
    total = sum(clientes for _, clientes, _, _ in resumen)

    print("ANÁLISIS POR NAVEGADOR")
    print("-" * 91)
    print(
        f"{'Navegador':<16} {'Clientes':>10} {'Distribución':>14} "
        f"{'Total compras':>15} {'Ventas totales':>18}"
    )
    print("-" * 91)
    for codigo, nombre in NAVEGADORES.items():
        cantidad, compras, ventas = metricas.get(
            codigo, (0, 0, Decimal("0"))
        )
        porcentaje = cantidad / total * 100
        print(
            f"{nombre:<16} {cantidad:>10} {porcentaje:>13.2f}% "
            f"{compras:>15} {ventas:>18,.3f}"
        )

    cantidades = {
        codigo: metricas.get(codigo, (0, 0, Decimal("0")))[0]
        for codigo in NAVEGADORES
    }
    frecuencia_maxima = max(cantidades.values())
    frecuencia_minima = min(cantidades.values())
    mas_utilizados = [
        NAVEGADORES[codigo]
        for codigo, cantidad in cantidades.items()
        if cantidad == frecuencia_maxima
    ]
    menos_utilizados = [
        nombre
        for codigo, nombre in NAVEGADORES.items()
        if cantidades[codigo] == frecuencia_minima
    ]

    total_compras_maximo = max(datos[1] for datos in metricas.values())
    mayor_numero_compras = [
        NAVEGADORES[codigo]
        for codigo, datos in metricas.items()
        if datos[1] == total_compras_maximo
    ]
    total_compras_minimo = min(datos[1] for datos in metricas.values())
    menor_numero_compras = [
        NAVEGADORES[codigo]
        for codigo, datos in metricas.items()
        if datos[1] == total_compras_minimo
    ]

    print(
        f"\nNavegador con mayor cantidad de clientes: "
        f"{', '.join(mas_utilizados)}"
    )
    print(
        f"Navegador con menor cantidad de clientes: "
        f"{', '.join(menos_utilizados)}"
    )
    print(
        f"Navegador con mayor número total de compras: "
        f"{', '.join(mayor_numero_compras)}"
    )
    print(
        f"Navegador con menor número total de compras: "
        f"{', '.join(menor_numero_compras)}"
    )

    modas = multimode(tiempos)
    print("\nESTADÍSTICAS DE TIEMPO")
    print("-" * 46)
    print(f"Media:   {mean(tiempos):.2f}")
    print(f"Mediana: {median(tiempos):.2f}")
    print(f"Moda:    {', '.join(f'{valor:g}' for valor in modas)}")


def main() -> None:
    cargar_configuracion()
    resumen, tiempos = cargar_datos()
    mostrar_resultados(resumen, tiempos)


if __name__ == "__main__":
    main()
