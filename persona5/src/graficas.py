from pathlib import Path

import matplotlib.pyplot as plt

from analisis import cargar_datos, compras_por_genero, metodo_pago_por_genero

OUT_DIR = Path(__file__).resolve().parent.parent / "graficas"


def grafica_compras_por_genero(df):
    resumen = compras_por_genero(df)
    fig, ax = plt.subplots(figsize=(6, 4))
    barras = ax.bar(resumen.index, resumen["count"], color=["#4C72B0", "#DD8452"])
    ax.set_title("Cantidad de clientes por género")
    ax.set_xlabel("Género")
    ax.set_ylabel("Número de clientes")
    for barra in barras:
        altura = barra.get_height()
        ax.annotate(
            f"{int(altura)}",
            (barra.get_x() + barra.get_width() / 2, altura),
            ha="center",
            va="bottom",
        )
    fig.tight_layout()
    fig.savefig(OUT_DIR / "compras_por_genero.png", dpi=150)
    plt.close(fig)


def grafica_metodo_pago_por_genero(df):
    tabla = metodo_pago_por_genero(df)
    fig, ax = plt.subplots(figsize=(7, 4))
    tabla.T.plot(kind="bar", ax=ax, color=["#4C72B0", "#DD8452"])
    ax.set_title("Método de pago preferido según género")
    ax.set_xlabel("Método de pago")
    ax.set_ylabel("Número de clientes")
    ax.legend(title="Género")
    for contenedor in ax.containers:
        ax.bar_label(contenedor)
    plt.xticks(rotation=0)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "metodo_pago_por_genero.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    df = cargar_datos()
    grafica_compras_por_genero(df)
    grafica_metodo_pago_por_genero(df)
    print("Gráficas guardadas en:", OUT_DIR)
