from __future__ import annotations

import csv
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import psycopg
from dotenv import load_dotenv


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

DATE_FORMAT = "%d.%m.%y"


def required(row: dict[str, str], column: str, line_number: int) -> str:
    value = row.get(column)
    if value is None or value.strip() == "":
        raise ValueError(
            f"Línea {line_number}: la columna '{column}' está vacía."
        )
    return value.strip()


def parse_int(row: dict[str, str], column: str, line_number: int) -> int:
    value = required(row, column, line_number)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(
            f"Línea {line_number}: '{column}' debe ser entero, recibido: {value!r}."
        ) from exc


def parse_decimal(row: dict[str, str], column: str, line_number: int) -> Decimal:
    value = required(row, column, line_number)
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(
            f"Línea {line_number}: '{column}' debe ser decimal, recibido: {value!r}."
        ) from exc


def parse_date(row: dict[str, str], column: str, line_number: int):
    value = required(row, column, line_number)
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError(
            f"Línea {line_number}: '{column}' debe usar formato DD.MM.YY, recibido: {value!r}."
        ) from exc


def validate_domain(name: str, value: int, allowed: set[int], line_number: int) -> None:
    if value not in allowed:
        raise ValueError(
            f"Línea {line_number}: '{name}'={value} no pertenece a {sorted(allowed)}."
        )


def parse_row(row: dict[str, str], line_number: int) -> tuple:
    id_cliente = parse_int(row, "Id_cliente", line_number)
    edad = parse_int(row, "Edad", line_number)
    genero = parse_int(row, "Genero", line_number)
    venta_total = parse_decimal(row, "Venta_total", line_number)
    n_compras = parse_int(row, "N_Compras", line_number)
    fecha_compra = parse_date(row, "FechaCompra", line_number)
    monto_compra = parse_decimal(row, "MontoCompra", line_number)
    metodo_pago = parse_int(row, "MetodoPago", line_number)
    tiempo = parse_int(row, "Tiempo", line_number)
    navegador = parse_int(row, "Navegador", line_number)
    boletin = parse_int(row, "Boletin", line_number)
    vale = parse_int(row, "Vale", line_number)

    if id_cliente <= 0:
        raise ValueError(f"Línea {line_number}: Id_cliente debe ser positivo.")
    if not 0 <= edad <= 120:
        raise ValueError(f"Línea {line_number}: Edad fuera del rango 0-120.")
    if venta_total < 0:
        raise ValueError(f"Línea {line_number}: Venta_total no puede ser negativa.")
    if n_compras < 0:
        raise ValueError(f"Línea {line_number}: N_Compras no puede ser negativa.")
    if monto_compra < 0:
        raise ValueError(f"Línea {line_number}: MontoCompra no puede ser negativo.")
    if tiempo < 0:
        raise ValueError(f"Línea {line_number}: Tiempo no puede ser negativo.")

    validate_domain("Genero", genero, {0, 1}, line_number)
    validate_domain("MetodoPago", metodo_pago, {0, 1, 2}, line_number)
    validate_domain("Navegador", navegador, {0, 1, 2, 3, 4}, line_number)
    validate_domain("Boletin", boletin, {0, 1}, line_number)
    validate_domain("Vale", vale, {0, 1}, line_number)

    return (
        id_cliente,
        edad,
        genero,
        venta_total,
        n_compras,
        fecha_compra,
        monto_compra,
        metodo_pago,
        tiempo,
        navegador,
        boletin,
        vale,
    )


def read_and_validate_csv(csv_path: Path) -> list[tuple]:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"No se encontró el CSV en: {csv_path.resolve()}"
        )

    records: list[tuple] = []
    seen_ids: set[int] = set()

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")

        if reader.fieldnames is None:
            raise ValueError("El CSV no contiene encabezados.")

        missing = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
        extra = [c for c in reader.fieldnames if c not in EXPECTED_COLUMNS]

        if missing or extra:
            raise ValueError(
                "Encabezados inesperados.\n"
                f"Faltantes: {missing or 'ninguno'}\n"
                f"Adicionales: {extra or 'ninguno'}"
            )

        # La primera fila de datos es la línea 2 del archivo.
        for line_number, row in enumerate(reader, start=2):
            record = parse_row(row, line_number)
            id_cliente = record[0]

            if id_cliente in seen_ids:
                raise ValueError(
                    f"Línea {line_number}: Id_cliente duplicado: {id_cliente}."
                )

            seen_ids.add(id_cliente)
            records.append(record)

    if not records:
        raise ValueError("El CSV no contiene registros.")

    return records


def get_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "sog2_ventas"),
        user=os.getenv("POSTGRES_USER", "sog2_user"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def load_records(records: list[tuple]) -> None:
    columns = """
        id_cliente,
        edad,
        genero,
        venta_total,
        n_compras,
        fecha_compra,
        monto_compra,
        metodo_pago,
        tiempo,
        navegador,
        boletin,
        vale
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE ventas_online;")

            with cur.copy(
                f"COPY ventas_online ({columns}) FROM STDIN"
            ) as copy:
                for record in records:
                    copy.write_row(record)

            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_registros,
                    COUNT(DISTINCT id_cliente) AS clientes_unicos,
                    MIN(edad) AS edad_minima,
                    MAX(edad) AS edad_maxima,
                    MIN(fecha_compra) AS fecha_minima,
                    MAX(fecha_compra) AS fecha_maxima
                FROM ventas_online;
                """
            )
            result = cur.fetchone()

    print("Carga completada correctamente.")
    print(f"Registros:       {result[0]}")
    print(f"Clientes únicos: {result[1]}")
    print(f"Edad mínima:     {result[2]}")
    print(f"Edad máxima:     {result[3]}")
    print(f"Fecha mínima:    {result[4]}")
    print(f"Fecha máxima:    {result[5]}")


def main() -> None:
    load_dotenv()

    csv_path = Path(
        os.getenv("CSV_PATH", "data/raw/Venta_online_c.csv")
    )

    print(f"Validando CSV: {csv_path}")
    records = read_and_validate_csv(csv_path)
    print(f"CSV válido. Registros listos para cargar: {len(records)}")

    load_records(records)


if __name__ == "__main__":
    main()
