# Persona 1: ventas por mes y estadisticas

## Limpieza y validacion

- Registros analizados: 6,500
- Columnas: 12
- `Venta_total`: valores numericos, sin nulos y sin negativos.
- `FechaCompra`: fechas validas entre 2021-01-01 y 2021-12-31.
- `Id_cliente`: sin duplicados.

## Analisis

La venta total acumulada fue **1,340,575.800**, con media **206.242**, mediana **137.350** y moda **98.000**. El valor minimo fue **9.000** y el maximo **3,169.000**.

| Mes | Registros | Ventas totales | Media | Mediana | Moda |
|---|---:|---:|---:|---:|---:|
| Enero | 520 | 106,059.700 | 203.961 | 132.050 | 141.600 |
| Febrero | 545 | 108,962.100 | 199.930 | 133.400 | 49.300 |
| Marzo | 569 | 116,168.000 | 204.162 | 135.000 | 38.600 |
| Abril | 557 | 116,737.700 | 209.583 | 137.300 | 22.100 |
| Mayo | 530 | 112,533.800 | 212.328 | 145.500 | 69.400 |
| Junio | 543 | 112,153.900 | 206.545 | 133.100 | 35.700 |
| Julio | 565 | 113,645.100 | 201.142 | 132.200 | 49.300 |
| Agosto | 530 | 105,665.000 | 199.368 | 136.100 | 39.200 |
| Septiembre | 508 | 109,666.700 | 215.879 | 145.200 | 22.100 |
| Octubre | 563 | 115,559.600 | 205.257 | 141.100 | 68.600 |
| Noviembre | 493 | 99,385.500 | 201.593 | 136.200 | 98.000 |
| Diciembre | 577 | 124,038.700 | 214.972 | 143.700 | 64.700 |

El mes con mayores ventas fue **Diciembre**, con **124,038.700**. El mes con menores ventas fue **Noviembre**, con **99,385.500**. La diferencia relativa entre ambos meses fue de **24.8%**.

## Graficas

- [Ventas totales por mes](../graficas/ventas_totales_por_mes.png)
- [Evolucion de ventas durante el ano](../graficas/evolucion_ventas_anual.png)

## Conclusion

Las ventas se distribuyeron durante los doce meses de 2021, pero no de manera uniforme. **Diciembre** concentró el mayor total y **Noviembre** el menor. La media superior a la mediana indica que algunos registros de Venta_total altos elevan el promedio.

## Recomendaciones

1. Reforzar inventario y campañas antes de **Diciembre**, tomando ese mes como referencia de demanda alta.
2. Investigar las causas de la baja observada en **Noviembre** y probar promociones o acciones comerciales específicas, comparando sus resultados con meses similares.

## Respuesta a la Pregunta A

La venta total mensual permite identificar la estacionalidad y priorizar recursos: se debe preparar la operación para el mes de mayor facturacion y usar el mes de menor facturacion como punto de partida para experimentar mejoras.

## Datos para reproducibilidad

Los calculos se generan desde `Venta_online_c.csv` con separador punto y coma, conservando el CSV original sin modificaciones.
