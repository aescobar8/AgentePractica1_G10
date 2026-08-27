import pandas as pd

from db import get_connection

GENERO_LABEL = {0: "Masculino", 1: "Femenino"}
METODO_LABEL = {0: "Efectivo", 1: "Tarjeta de Crédito", 2: "Tarjeta de Débito"}


def cargar_datos():
    with get_connection() as conn:
        return pd.read_sql(
            "SELECT genero, n_compras, metodo_pago FROM ventas_online", conn
        )


def estadisticas_n_compras(df):
    return {
        "media": df["n_compras"].mean(),
        "mediana": df["n_compras"].median(),
        "moda": df["n_compras"].mode().iloc[0],
    }


def compras_por_genero(df):
    resumen = df.groupby("genero")["n_compras"].agg(["count", "sum", "mean"])
    resumen.index = resumen.index.map(GENERO_LABEL)
    return resumen


def metodo_pago_por_genero(df):
    tabla = pd.crosstab(df["genero"], df["metodo_pago"])
    tabla.index = tabla.index.map(GENERO_LABEL)
    tabla.columns = tabla.columns.map(METODO_LABEL)
    return tabla


if __name__ == "__main__":
    df = cargar_datos()
    print("Estadísticas N_Compras:", estadisticas_n_compras(df))
    print("\nCompras por género:\n", compras_por_genero(df))
    print("\nMétodo de pago por género:\n", metodo_pago_por_genero(df))
