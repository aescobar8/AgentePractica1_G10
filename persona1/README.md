# Persona 1 - Ventas por mes y estadisticas

Este modulo analiza `Venta_total` y `FechaCompra` del CSV compartido.

## Ejecucion

Desde la raiz del repositorio:

```powershell
py -m pip install -r persona1/requirements.txt
py persona1/analisis/analisis_ventas.py
py persona1/graficas/graficas_ventas.py
```

Por defecto se utiliza `persona4/sog2_postgres_local/data/raw/Venta_online_c.csv`.
Se puede indicar otro CSV con `--csv`.

## Entregables

- `resultados/analisis_persona1.md`: limpieza, estadisticas, analisis, conclusion, recomendaciones y respuesta a la Pregunta A.
- `resultados/ventas_por_mes.csv`: ventas y estadisticas por mes.
- `graficas/ventas_totales_por_mes.png`: ventas totales por mes con valores visibles.
- `graficas/evolucion_ventas_anual.png`: evolucion mensual de ventas con valores visibles.
- `database/consultas_ventas.sql`: consultas equivalentes para PostgreSQL.
- `ia_mcp/herramientas_ventas.py`: herramientas que el MCP comun descubre automaticamente.

La limpieza valida encabezados, nulos, tipos numericos, fechas validas de 2021,
duplicados de `Id_cliente` y valores no negativos de `Venta_total`.
