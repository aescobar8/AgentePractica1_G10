import pandas as pd

from db import get_connection


def cargar_datos():
    with get_connection() as conn:
        return pd.read_sql(
            "SELECT id_cliente, genero, n_compras FROM ventas_online", conn
        )


def validar_limpieza(df):
    return {
        "filas": len(df),
        "nulos_genero": int(df["genero"].isna().sum()),
        "nulos_n_compras": int(df["n_compras"].isna().sum()),
        "duplicados_id_cliente": int(df["id_cliente"].duplicated().sum()),
        "valores_genero": sorted(df["genero"].unique().tolist()),
        "n_compras_min": int(df["n_compras"].min()),
        "n_compras_max": int(df["n_compras"].max()),
    }


if __name__ == "__main__":
    df = cargar_datos()
    for clave, valor in validar_limpieza(df).items():
        print(f"{clave}: {valor}")
