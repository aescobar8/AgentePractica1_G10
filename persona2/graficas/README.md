# Gráficas de Persona 2

- `distribucion_ventas_metodo_pago.png`: gráfico circular tipo donut con cantidad
  y porcentaje exacto de ventas/registros por método.
- `comparacion_montos_metodo_pago.png`: gráfica de densidad que compara la
  distribución de `MontoCompra` entre los tres métodos, acompañada por la media,
  mediana y cantidad exacta de registros de cada grupo.

Para generarlas:

```powershell
py persona2/graficas/graficas_metodos_pago.py
```
