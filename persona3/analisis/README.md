# Análisis de navegador y tiempo

El script `analisis_navegador_tiempo.py` consulta la tabla `ventas_online` de
PostgreSQL y calcula:

- cantidad de clientes o registros por navegador (`COUNT(*)`);
- distribución porcentual de clientes por navegador;
- cantidad total de compras por navegador (`SUM(n_compras)`);
- ventas totales por navegador (`SUM(venta_total)`);
- navegador con mayor y menor cantidad de clientes/registros;
- navegador con mayor y menor número total de compras;
- media, mediana y moda de `Tiempo`.

## Configuración

El programa carga primero la configuración compartida de
`persona4/sog2_postgres_local/.env`. Si existe `persona3/.env`, sus valores
sobrescriben la configuración compartida. Las variables utilizadas son:

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_SSLMODE` (opcional para la conexión en la nube)

## Ejecución

Desde la raíz del repositorio:

```powershell
py -m pip install -r persona3/analisis/requirements.txt
py persona3/analisis/analisis_navegador_tiempo.py
```
