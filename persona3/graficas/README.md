# Gráficas de navegador y tiempo

El script consulta `ventas_online` en PostgreSQL mediante la configuración de
`.env` y genera dos imágenes:

- `distribucion_compras_por_navegador.png`: gráfica circular basada en
  `SUM(n_compras)` por navegador.
- `boxplot_tiempo_por_navegador.png`: distribución de `tiempo` agrupada por
  navegador, con una tabla que identifica los registros, mínimo, cuartiles,
  mediana, media y máximo de cada grupo.

El archivo `graficas_navegador_2.py` genera además:

- `ventas_compras_por_navegador.png`: dos paneles con compras y ventas totales
  por navegador, mostrando los valores exactos.
- `comparacion_resultados_navegadores.png`: comparación porcentual de clientes,
  compras y ventas, acompañada por una tabla con los totales exactos.

Desde la raíz del repositorio:

```powershell
py -m pip install -r persona3/graficas/requirements.txt
py persona3/graficas/graficas_navegador.py
py persona3/graficas/graficas_navegador_2.py
```
