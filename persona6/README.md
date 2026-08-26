# Persona 6: boletines y vales

Esta carpeta contiene el análisis reproducible, las gráficas, las consultas SQL y las funciones que pueden registrarse en el agente IA/MCP para la parte de boletines y vales.

## Ejecutar el análisis

Desde la raíz del repositorio:

    python -m pip install -r persona6/requirements.txt
    python persona6/scripts/analisis_boletines_vales.py

El script lee Venta_online_c.csv, valida los datos, genera las dos gráficas y escribe el informe en persona6/resultados/analisis_persona6.md.

## Entregables generados

- persona6/graficas/uso_boletines_vales_por_mes.png
- persona6/graficas/relacion_boletin_vale.png
- persona6/resultados/analisis_persona6.md
- persona6/resultados/metricas_persona6.json
- persona6/resultados/uso_mensual_boletines_vales.csv
- persona6/resultados/patrones_compra_promociones.csv
- persona6/resultados/relacion_boletin_vale.csv

## Base de datos e IA/MCP

Las consultas para PostgreSQL están en database/consultas_boletines_vales.sql.

El módulo ia_mcp/herramientas_boletines_vales.py expone cuatro funciones:

- resumen_boletines_vales
- uso_mensual_boletines_vales
- patrones_compra_promociones
- relacion_boletin_vale

Cada función recibe una conexión DB-API compatible con psycopg y devuelve diccionarios serializables. TOOL_DEFINITIONS y dispatch_tool permiten registrarlas en el servidor MCP existente sin asumir una implementación específica de Google ADK.
