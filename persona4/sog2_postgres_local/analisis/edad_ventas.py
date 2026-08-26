from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg
from dotenv import load_dotenv
from scipy.stats import pearsonr, spearmanr


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "resultados" / "persona4"

GRUPOS_EDAD = [17, 24, 34, 44, 54, 64, 120]
ETIQUETAS_EDAD = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]


# ---------------------------------------------------------------------------
# Acceso a datos
# ---------------------------------------------------------------------------

def obtener_conexion() -> psycopg.Connection:
    load_dotenv(BASE_DIR / ".env")

    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError(
            "No se encontró POSTGRES_PASSWORD. Verifica que exista el archivo .env."
        )

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "sog2_ventas"),
        user=os.getenv("POSTGRES_USER", "sog2_user"),
        password=password,
    )


def obtener_datos() -> pd.DataFrame:
    consulta = """
        SELECT
            id_cliente,
            edad,
            venta_total,
            n_compras,
            monto_compra
        FROM ventas_online
        ORDER BY id_cliente;
    """

    with obtener_conexion() as conn:
        with conn.cursor() as cursor:
            cursor.execute(consulta)
            filas = cursor.fetchall()
            columnas = [col.name for col in cursor.description]

    df = pd.DataFrame(filas, columns=columnas)

    for columna in ["venta_total", "monto_compra"]:
        df[columna] = pd.to_numeric(df[columna])
    return df

# Limpieza 

def validar_datos(df: pd.DataFrame) -> None:

    columnas_requeridas = {
        "id_cliente",
        "edad",
        "venta_total",
        "n_compras",
        "monto_compra",
    }

    faltantes = columnas_requeridas.difference(df.columns)
    if faltantes:
        raise ValueError(
            f"Faltan columnas necesarias para el análisis: {sorted(faltantes)}"
        )

    if df.empty:
        raise ValueError("La consulta no devolvió registros.")

    if df["id_cliente"].isna().any():
        raise ValueError("Se encontraron valores nulos en Id_cliente.")

    if df["id_cliente"].duplicated().any():
        duplicados = df.loc[df["id_cliente"].duplicated(), "id_cliente"].tolist()
        raise ValueError(
            f"Se encontraron Id_cliente duplicados. Ejemplos: {duplicados[:10]}"
        )

    if df["edad"].isna().any():
        raise ValueError("Se encontraron valores nulos en Edad.")

    if not pd.api.types.is_integer_dtype(df["edad"]):
        raise ValueError("Edad debe contener valores enteros.")

    edades_invalidas = df.loc[~df["edad"].between(0, 120), "edad"]
    if not edades_invalidas.empty:
        raise ValueError(
            f"Se encontraron edades fuera del rango permitido: "
            f"{sorted(edades_invalidas.unique().tolist())}"
        )
    
    for columna in ["venta_total", "n_compras", "monto_compra"]:
        if df[columna].isna().any():
            raise ValueError(
                f"Se encontraron valores nulos en la columna requerida '{columna}'."
            )


# ---------------------------------------------------------------------------
# Análisis
# ---------------------------------------------------------------------------

def agregar_grupos_edad(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa a los clientes en rangos de edad fáciles de interpretar
    """
    resultado = df.copy()

    resultado["grupo_edad"] = pd.cut(
        resultado["edad"],
        bins=GRUPOS_EDAD,
        labels=ETIQUETAS_EDAD,
        include_lowest=True,
        right=True,
    )

    if resultado["grupo_edad"].isna().any():
        raise ValueError(
            "Hay edades que no pudieron asignarse a ningún grupo"
        )

    return resultado


def calcular_estadisticas_edad(df: pd.DataFrame) -> dict:
    """
    Calcula media, mediana y moda de Edad
    """
    modas = df["edad"].mode().tolist()

    return {
        "media": float(df["edad"].mean()),
        "mediana": float(df["edad"].median()),
        "moda": [int(valor) for valor in modas],
        "minima": int(df["edad"].min()),
        "maxima": int(df["edad"].max()),
    }


def calcular_resumen_por_grupo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resume el comportamiento de compra para cada grupo de edad

    Se usan varias métricas para no confundir "comprar más" con tener
    simplemente una mayor cantidad de clientes.
    """
    resumen = (
        df.groupby("grupo_edad", observed=False)
        .agg(
            clientes=("id_cliente", "nunique"),
            venta_total=("venta_total", "sum"),
            venta_promedio=("venta_total", "mean"),
            compras_totales=("n_compras", "sum"),
            compras_promedio=("n_compras", "mean"),
            monto_compra_promedio=("monto_compra", "mean"),
        )
        .reset_index()
    )

    columnas_decimales = [
        "venta_total",
        "venta_promedio",
        "compras_promedio",
        "monto_compra_promedio",
    ]
    resumen[columnas_decimales] = resumen[columnas_decimales].round(2)

    return resumen


def calcular_correlacion_edad_ventas(df: pd.DataFrame) -> dict:
    """
    Analiza la relación entre Edad y Venta_total con Pearson y Spearman.
    """
    pearson_r, pearson_p = pearsonr(df["edad"], df["venta_total"])
    spearman_rho, spearman_p = spearmanr(df["edad"], df["venta_total"])

    return {
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
        "spearman_rho": float(spearman_rho),
        "spearman_p": float(spearman_p),
    }


def identificar_extremos(resumen: pd.DataFrame) -> dict:
    """
    Identifica los grupos con mayor y menor comportamiento según
    diferentes métricas. No crea un índice artificial de comportamiento.
    """
    return {
        "mayor_venta_total": str(
            resumen.loc[resumen["venta_total"].idxmax(), "grupo_edad"]
        ),
        "menor_venta_total": str(
            resumen.loc[resumen["venta_total"].idxmin(), "grupo_edad"]
        ),
        "mayor_venta_promedio": str(
            resumen.loc[resumen["venta_promedio"].idxmax(), "grupo_edad"]
        ),
        "menor_venta_promedio": str(
            resumen.loc[resumen["venta_promedio"].idxmin(), "grupo_edad"]
        ),
        "mayor_compras_promedio": str(
            resumen.loc[resumen["compras_promedio"].idxmax(), "grupo_edad"]
        ),
        "menor_compras_promedio": str(
            resumen.loc[resumen["compras_promedio"].idxmin(), "grupo_edad"]
        ),
    }


# ---------------------------------------------------------------------------
# Gráficas
# ---------------------------------------------------------------------------

def generar_grafica_ventas_por_grupo(resumen: pd.DataFrame) -> Path:
    """
    Gráfica 1: ventas totales por grupos de edad.
    Muestra valores exactos sobre cada barra.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = OUTPUT_DIR / "01_ventas_por_grupo_edad.png"

    fig, ax = plt.subplots(figsize=(10, 6))

    barras = ax.bar(
        resumen["grupo_edad"].astype(str),
        resumen["venta_total"],
    )

    ax.set_title("Ventas totales por grupo de edad")
    ax.set_xlabel("Grupo de edad (años)")
    ax.set_ylabel("Venta total")
    ax.grid(axis="y", alpha=0.25)

    etiquetas = [
        f"{valor:,.2f}"
        for valor in resumen["venta_total"]
    ]
    ax.bar_label(
        barras,
        labels=etiquetas,
        padding=3,
        fontsize=9,
    )

    limite_superior = resumen["venta_total"].max() * 1.15
    ax.set_ylim(0, limite_superior)

    fig.tight_layout()
    fig.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return ruta


def generar_grafica_dispersion(
    df: pd.DataFrame,
    correlacion: dict,
) -> Path:
    """
    Gráfica 2: dispersión Edad vs Venta_total.
    Se agrega una línea de tendencia para facilitar la interpretación.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = OUTPUT_DIR / "02_edad_vs_venta_total.png"

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(
        df["edad"],
        df["venta_total"],
        alpha=0.30,
        s=18,
    )

    pendiente, intercepto = np.polyfit(
        df["edad"],
        df["venta_total"],
        1,
    )

    x = np.linspace(df["edad"].min(), df["edad"].max(), 100)
    y = pendiente * x + intercepto

    ax.plot(x, y, linewidth=2)

    ax.set_title("Relación entre edad y venta total")
    ax.set_xlabel("Edad (años)")
    ax.set_ylabel("Venta total")
    ax.grid(alpha=0.25)

    texto = (
        f"Pearson r = {correlacion['pearson_r']:.4f}\n"
        f"Spearman ρ = {correlacion['spearman_rho']:.4f}"
    )

    ax.text(
        0.02,
        0.98,
        texto,
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round", "alpha": 0.15},
    )

    fig.tight_layout()
    fig.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return ruta


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

def imprimir_resultados(
    estadisticas: dict,
    resumen: pd.DataFrame,
    correlacion: dict,
    extremos: dict,
) -> None:
    print("\n" + "=" * 68)
    print("PERSONA 4 - EDAD Y VENTAS")
    print("=" * 68)

    print("\n1. Estadísticas de Edad")
    print(f"   Media:   {estadisticas['media']:.2f} años")
    print(f"   Mediana: {estadisticas['mediana']:.2f} años")
    print(
        "   Moda:    "
        + ", ".join(str(valor) for valor in estadisticas["moda"])
        + " años"
    )
    print(f"   Mínima:  {estadisticas['minima']} años")
    print(f"   Máxima:  {estadisticas['maxima']} años")

    print("\n2. Resumen por grupos de edad")
    print(resumen.to_string(index=False))

    print("\n3. Grupos destacados")
    print(
        f"   Mayor venta total:        {extremos['mayor_venta_total']}"
    )
    print(
        f"   Menor venta total:        {extremos['menor_venta_total']}"
    )
    print(
        f"   Mayor venta promedio:     {extremos['mayor_venta_promedio']}"
    )
    print(
        f"   Menor venta promedio:     {extremos['menor_venta_promedio']}"
    )
    print(
        f"   Mayor promedio compras:   {extremos['mayor_compras_promedio']}"
    )
    print(
        f"   Menor promedio compras:   {extremos['menor_compras_promedio']}"
    )

    print("\n4. Relación Edad vs Venta_total")
    print(
        f"   Pearson r:    {correlacion['pearson_r']:.6f}"
        f" | p={correlacion['pearson_p']:.6f}"
    )
    print(
        f"   Spearman rho: {correlacion['spearman_rho']:.6f}"
        f" | p={correlacion['spearman_p']:.6f}"
    )

    if abs(correlacion["pearson_r"]) < 0.10:
        print(
            "   Interpretación: la relación lineal entre Edad y Venta_total "
            "es prácticamente nula."
        )


def guardar_resultados(
    resumen: pd.DataFrame,
    estadisticas: dict,
    correlacion: dict,
    extremos: dict,
) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ruta_csv = OUTPUT_DIR / "resumen_grupos_edad.csv"
    resumen.to_csv(
        ruta_csv,
        index=False,
        encoding="utf-8-sig",
    )

    ruta_txt = OUTPUT_DIR / "resultados_persona4.txt"

    with ruta_txt.open("w", encoding="utf-8") as archivo:
        archivo.write("PERSONA 4 - EDAD Y VENTAS\n")
        archivo.write("=" * 68 + "\n\n")

        archivo.write("Estadísticas de Edad\n")
        archivo.write(f"Media: {estadisticas['media']:.2f} años\n")
        archivo.write(f"Mediana: {estadisticas['mediana']:.2f} años\n")
        archivo.write(
            "Moda: "
            + ", ".join(str(valor) for valor in estadisticas["moda"])
            + " años\n"
        )
        archivo.write(f"Mínima: {estadisticas['minima']} años\n")
        archivo.write(f"Máxima: {estadisticas['maxima']} años\n\n")

        archivo.write("Resumen por grupos de edad\n")
        archivo.write(resumen.to_string(index=False))
        archivo.write("\n\n")

        archivo.write("Grupos destacados\n")
        for clave, valor in extremos.items():
            archivo.write(f"{clave}: {valor}\n")

        archivo.write("\nCorrelación Edad vs Venta_total\n")
        archivo.write(
            f"Pearson r: {correlacion['pearson_r']:.6f}, "
            f"p={correlacion['pearson_p']:.6f}\n"
        )
        archivo.write(
            f"Spearman rho: {correlacion['spearman_rho']:.6f}, "
            f"p={correlacion['spearman_p']:.6f}\n"
        )

    return ruta_csv, ruta_txt


# ---------------------------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------------------------

def ejecutar_analisis() -> dict:
    """
    Ejecuta todo el análisis de Persona 4.

    El diccionario retornado también facilita reutilizar estas funciones
    posteriormente desde el MCP Server.
    """
    df = obtener_datos()
    validar_datos(df)
    df = agregar_grupos_edad(df)

    estadisticas = calcular_estadisticas_edad(df)
    resumen = calcular_resumen_por_grupo(df)
    correlacion = calcular_correlacion_edad_ventas(df)
    extremos = identificar_extremos(resumen)

    grafica_1 = generar_grafica_ventas_por_grupo(resumen)
    grafica_2 = generar_grafica_dispersion(df, correlacion)

    ruta_csv, ruta_txt = guardar_resultados(
        resumen,
        estadisticas,
        correlacion,
        extremos,
    )

    imprimir_resultados(
        estadisticas,
        resumen,
        correlacion,
        extremos,
    )

    print("\nArchivos generados:")
    print(f" - {grafica_1}")
    print(f" - {grafica_2}")
    print(f" - {ruta_csv}")
    print(f" - {ruta_txt}")

    return {
        "estadisticas_edad": estadisticas,
        "resumen_grupos": resumen.to_dict(orient="records"),
        "correlacion": correlacion,
        "extremos": extremos,
    }


if __name__ == "__main__":
    ejecutar_analisis()
