# Persona 5 - Género y comportamiento de compra

Análisis de `Genero` y `N_Compras` sobre la base `sog2_ventas` (Postgres local,
levantada desde `persona4/sog2_postgres_local`).

## Uso

Con el contenedor `sog2-postgres` corriendo (`docker compose up -d` desde
`persona4/sog2_postgres_local`):

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python src\limpieza.py
python src\analisis.py
python src\graficas.py
```

Las gráficas se guardan en `persona5/graficas/`.

## Entregables

- `resultados/analisis_persona5.md`: análisis, conclusión, recomendaciones y respuesta a la Pregunta E.
- `graficas/compras_por_genero.png`, `graficas/metodo_pago_por_genero.png`.
- `database/consultas_genero.sql`: consultas SQL equivalentes al análisis.
- `ia_mcp/herramientas_genero.py`: funciones (`resumen_genero`, `estadisticas_n_compras`, `metodo_pago_por_genero`) listas para registrarse en el MCP Server, con el mismo patrón que `persona6/ia_mcp`.
