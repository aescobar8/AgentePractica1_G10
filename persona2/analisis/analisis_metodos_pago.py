from __future__ import annotations

import os
from pathlib import Path
from statistics import mean, median, multimode

import psycopg
from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[2]
SHARED_ENV = REPO_ROOT / "persona4" / "sog2_postgres_local" / ".env"
PERSONA2_ENV = REPO_ROOT / "persona2" / ".env"

METODOS_PAGO = {
    0: "Efectivo/contra entrega",
    1: "Tarjeta de Crédito",
    2: "Tarjeta de Débito",
}


def cargar_configuracion() -> None:
    """Carga la conexión común y permite sobrescribirla con persona2/.env."""
    load_dotenv(SHARED_ENV)
    load_dotenv(PERSONA2_ENV, override=True)


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
        raise ValueError("Faltan variables de conexión: " + ", ".join(faltantes))

    if os.getenv("POSTGRES_SSLMODE"):
        parametros["sslmode"] = os.getenv("POSTGRES_SSLMODE")
    return psycopg.connect(**parametros)


def cargar_y_limpiar_datos() -> list[tuple[int, float]]:
    """Obtiene únicamente MetodoPago y MontoCompra y valida sus dominios."""
    with conectar() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT metodo_pago, monto_compra
                FROM ventas_online
                WHERE metodo_pago IS NOT NULL AND monto_compra IS NOT NULL
                ORDER BY id_cliente;
                """
            )
            filas = [(int(metodo), float(monto)) for metodo, monto in cursor.fetchall()]

    if not filas:
        raise ValueError("No hay registros válidos para analizar.")

    invalidos = [fila for fila in filas if fila[0] not in METODOS_PAGO or fila[1] < 0]
    if invalidos:
        raise ValueError(
            f"Se encontraron {len(invalidos)} registros con método o monto inválido."
        )
    return filas


def mostrar_resultados(filas: list[tuple[int, float]]) -> None:
    total_registros = len(filas)
    montos = [monto for _, monto in filas]
    resumen: dict[int, dict[str, float | int]] = {}

    for codigo in METODOS_PAGO:
        montos_metodo = [monto for metodo, monto in filas if metodo == codigo]
        resumen[codigo] = {
            "registros": len(montos_metodo),
            "total": sum(montos_metodo),
            "media": mean(montos_metodo) if montos_metodo else 0,
            "mediana": median(montos_metodo) if montos_metodo else 0,
        }

    print("ANÁLISIS DE MÉTODOS DE PAGO")
    print("-" * 94)
    print(
        f"{'Método':<26} {'Registros':>10} {'Distribución':>14} "
        f"{'Monto total':>16} {'Media':>12} {'Mediana':>12}"
    )
    print("-" * 94)
    for codigo, nombre in METODOS_PAGO.items():
        datos = resumen[codigo]
        porcentaje = int(datos["registros"]) / total_registros * 100
        print(
            f"{nombre:<26} {int(datos['registros']):>10} {porcentaje:>13.2f}% "
            f"{float(datos['total']):>16,.3f} {float(datos['media']):>12,.3f} "
            f"{float(datos['mediana']):>12,.3f}"
        )

    maxima_frecuencia = max(int(datos["registros"]) for datos in resumen.values())
    mas_utilizados = [
        METODOS_PAGO[codigo]
        for codigo, datos in resumen.items()
        if int(datos["registros"]) == maxima_frecuencia
    ]

    modas = multimode(montos)
    print(f"\nMétodo de pago más utilizado: {', '.join(mas_utilizados)}")
    print(
        "Total pagado en efectivo/contra entrega: "
        f"{float(resumen[0]['total']):,.3f}"
    )
    print("\nESTADÍSTICAS GENERALES DE MONTOCOMPRA")
    print(f"Media:   {mean(montos):,.3f}")
    print(f"Mediana: {median(montos):,.3f}")
    print("Moda:    " + ", ".join(f"{valor:,.3f}" for valor in modas))


def main() -> None:
    cargar_configuracion()
    mostrar_resultados(cargar_y_limpiar_datos())


if __name__ == "__main__":
    main()

