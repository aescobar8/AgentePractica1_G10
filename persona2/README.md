# Persona 2 — Métodos de pago

La carpeta contiene el análisis asignado a Persona 2 usando los campos
`MetodoPago` y `MontoCompra` almacenados en PostgreSQL.

## Contenido

- `analisis/`: limpieza, validación y cálculos estadísticos.
- `graficas/`: distribución de ventas y comparación de montos.
- `ia_mcp/`: tres herramientas registradas automáticamente por el MCP común.
- `.env.example`: ejemplo sin credenciales reales.
- `requirements.txt`: dependencias de Python.

Los códigos se interpretan así: 0 = efectivo/contra entrega, 1 = tarjeta de
crédito y 2 = tarjeta de débito.

El programa utiliza primero la conexión compartida ubicada en
`persona4/sog2_postgres_local/.env`. Si existe `persona2/.env`, sus valores
sobrescriben la configuración compartida.

## Ejecución

```powershell
py -m pip install -r persona2/requirements.txt
py persona2/analisis/analisis_metodos_pago.py
py persona2/graficas/graficas_metodos_pago.py
```

No se debe subir ningún archivo `.env` a Git.
