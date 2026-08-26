# Análisis de métodos de pago

Este módulo consulta desde PostgreSQL en la nube únicamente `metodo_pago` y
`monto_compra`. Elimina valores nulos mediante la consulta y valida que el método
sea 0, 1 o 2 y que el monto no sea negativo.

Calcula la distribución de registros y el monto acumulado por método, identifica
el método más utilizado, suma lo pagado en efectivo/contra entrega, obtiene media,
mediana y moda de `MontoCompra` y compara la media y mediana entre métodos.

Desde la raíz del repositorio:

```powershell
py -m pip install -r persona2/requirements.txt
py persona2/analisis/analisis_metodos_pago.py
```

