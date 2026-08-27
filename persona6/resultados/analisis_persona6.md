# Persona 6: análisis de boletines y vales

## Alcance

Esta sección analiza el uso de las columnas Boletin y Vale, su comportamiento mensual, los patrones de compra asociados y la relación entre ambas promociones. Cada fila representa un Id_cliente único según la validación realizada.

## Validación y limpieza

- Archivo procesado: C:\Users\marco\Desktop\Carrera\2S2026\GEREN 2\LAB\AgentePractica1_G10\Venta_online_c.csv
- Registros analizados: 6,500
- Columnas: 12
- Fechas válidas: 2021-01-01 a 2021-12-31
- Valores faltantes o inválidos: 0
- Id_cliente duplicados: 0
- Dominio Boletin: 0 = No, 1 = Sí
- Dominio Vale: 0 = No, 1 = Sí

La limpieza consistió en leer el archivo con separador punto y coma y codificación UTF-8 con BOM, convertir las variables numéricas a tipos numéricos, transformar FechaCompra al formato de fecha y validar que Boletin y Vale solo contuvieran 0 o 1. No fue necesario eliminar registros porque las 6,500 filas cumplieron las reglas.

## Resumen general

| Indicador | Resultado |
|---|---:|
| Registros totales | 6,500 |
| Usaron boletín | 2,921 (44.9%) |
| Usaron vale | 1,254 (19.3%) |
| Usaron ambos | 811 (12.5%) |
| No usaron ninguno | 3,136 (48.2%) |

## Uso por mes

El mes con mayor uso de boletines fue **Diciembre**, con **262** clientes. El mes con mayor uso de vales fue **Marzo**, con **133** clientes.

| Mes | Registros | Boletines | % boletines | Vales | % vales |
|---|---:|---:|---:|---:|---:|
| Enero | 520 | 241 | 46.3% | 100 | 19.2% |
| Febrero | 545 | 259 | 47.5% | 91 | 16.7% |
| Marzo | 569 | 261 | 45.9% | 133 | 23.4% |
| Abril | 557 | 239 | 42.9% | 88 | 15.8% |
| Mayo | 530 | 251 | 47.4% | 97 | 18.3% |
| Junio | 543 | 228 | 42.0% | 102 | 18.8% |
| Julio | 565 | 236 | 41.8% | 96 | 17.0% |
| Agosto | 530 | 251 | 47.4% | 102 | 19.2% |
| Septiembre | 508 | 200 | 39.4% | 120 | 23.6% |
| Octubre | 563 | 260 | 46.2% | 85 | 15.1% |
| Noviembre | 493 | 233 | 47.3% | 112 | 22.7% |
| Diciembre | 577 | 262 | 45.4% | 128 | 22.2% |

Gráfica mensual: [uso_boletines_vales_por_mes.png](../graficas/uso_boletines_vales_por_mes.png)

## Patrones de compra

Los segmentos se definieron así: Ninguno no usa ninguna promoción; Solo boletín usa boletín pero no vale; Solo vale usa vale pero no boletín; Ambos usa las dos promociones.

| Segmento | Clientes | % | Venta total media | Mediana venta | Compras medias | Monto medio |
|---|---:|---:|---:|---:|---:|---:|
| Ninguno | 3,136 | 48.2% | 183.331 | 121.800 | 4.600 | 38.265 |
| Solo boletín | 2,110 | 32.5% | 233.802 | 154.600 | 5.751 | 38.979 |
| Solo vale | 443 | 6.8% | 170.657 | 114.000 | 4.287 | 43.619 |
| Ambos | 811 | 12.5% | 242.572 | 173.300 | 5.704 | 45.681 |

El segmento Ambos presenta la mayor venta total media (242.572) y la mayor mediana de venta (173.300). El segmento Ninguno representa la mayor cantidad de registros (3,136), por lo que existe una oportunidad para estudiar campañas de incorporación. El segmento Solo vale tiene el menor promedio de compras (4.287), aunque registra un monto medio de compra superior al segmento Ninguno.

## Relación entre boletín y vale

| Uso de boletín | No usa vale | Usa vale | Total |
|---|---:|---:|---:|
| No | 3,136 | 443 | 3,579 |
| Sí | 2,110 | 811 | 2,921 |

La probabilidad de usar vale entre quienes recibieron o utilizaron boletín fue **27.8%**, frente a **12.4%** entre quienes no usaron boletín. Esto representa un lift de **2.24**. La correlación phi de **0.194** indica una asociación positiva baja; debe interpretarse como relación observada y no como causalidad.

Gráfica de relación: [relacion_boletin_vale.png](../graficas/relacion_boletin_vale.png)

## Conclusión

1. Se analizaron 6,500 registros correspondientes al CSV de ventas online de 2021.
2. El boletín aparece utilizado en 2,921 registros, equivalentes al 44.9% del total.
3. El vale aparece utilizado en 1,254 registros, equivalentes al 19.3% del total.
4. 811 clientes utilizaron simultáneamente boletín y vale.
5. 3,136 clientes no utilizaron ninguna de las dos promociones.
6. El uso de boletines alcanzó su máximo en Diciembre, con 262 clientes.
7. El uso de vales alcanzó su máximo en Marzo, con 133 clientes.
8. La utilización de boletines se mantuvo presente en todos los meses, sin concentrarse en un único periodo.
9. La utilización de vales fue menor que la de boletines en cada mes observado.
10. El segmento sin promociones registró una venta total media de 183.331.
11. El segmento que utilizó solo boletín registró una venta total media de 233.802.
12. El segmento que utilizó solo vale registró una venta total media de 170.657.
13. El segmento que utilizó ambas promociones obtuvo la venta total media más alta: 242.572.
14. Los clientes del segmento de ambas promociones realizaron 5.704 compras en promedio.
15. Los clientes que usaron solo vale realizaron 4.287 compras en promedio, el valor más bajo de los cuatro segmentos.
16. El monto medio de compra fue 45.681 para quienes usaron ambas promociones.
17. La correlación phi entre boletín y vale fue 0.194, positiva y de magnitud baja.
18. La probabilidad de usar vale fue 27.8% entre quienes usaron boletín.
19. Sin boletín, la probabilidad de usar vale bajó a 12.4%.
20. Los resultados muestran asociación entre las promociones, pero no prueban que una promoción cause directamente un mayor gasto.

## Recomendaciones

1. **Priorizar campañas diferenciadas por temporada.** Usar diciembre como referencia para campañas de boletines y marzo como referencia para campañas de vales, monitoreando también septiembre y noviembre, que presentan porcentajes mensuales altos de uso de vales. La ejecución debe medirse con grupos de control para distinguir asociación de efecto real.
2. **Diseñar una estrategia de conversión para clientes sin promociones.** El segmento Ninguno concentra 3,136 clientes (48.2%) y puede recibir pruebas segmentadas de boletín, vale o ambas promociones. Se deben comparar venta total, número de compras y monto medio antes de ampliar la campaña.

## Planificación del proyecto

La distribución acordada para trabajar en paralelo es:

| Responsable | Alcance acordado |
|---|---|
| Persona 1 | Ventas por mes y estadísticas de Venta_total. |
| Persona 2 | Métodos de pago y MontoCompra. |
| Persona 3 | Navegadores y Tiempo. |
| Persona 4 | Edad, Id_cliente y relación con ventas. |
| Persona 5 | Género, N_Compras y relación con método de pago. |
| Persona 6 | Boletines, vales, planificación y metodología del informe. |

La Persona 6 integra además la información que cada integrante entregue para consolidar las secciones de planificación y metodología, sin asumir la implementación completa de la base de datos, Google ADK o MCP Server.

## Metodología propuesta

1. Recibir el CSV original y conservar una copia sin modificaciones.
2. Validar codificación, separador, encabezados, cantidad de columnas y cantidad de registros.
3. Convertir FechaCompra al tipo fecha y derivar el mes de compra.
4. Validar valores faltantes, duplicados, tipos numéricos y dominios de Boletin y Vale.
5. Calcular conteos y porcentajes mensuales de uso.
6. Construir segmentos Ninguno, Solo boletín, Solo vale y Ambos.
7. Comparar venta total, número de compras y monto de compra entre segmentos.
8. Construir la tabla de contingencia Boletin x Vale y calcular probabilidades condicionales, lift y correlación phi.
9. Generar las dos gráficas con títulos, ejes, leyendas y valores exactos visibles.
10. Publicar consultas SQL y funciones IA/MCP que devuelvan los mismos resultados desde la base de datos.
11. Revisar que los resultados de las gráficas, tablas y consultas coincidan antes de integrarlos en el informe final.

## Funciones para IA/MCP

Las funciones de consulta se encuentran en [herramientas_boletines_vales.py](../ia_mcp/herramientas_boletines_vales.py) y cubren:

- resumen general de uso de boletines y vales;
- uso mensual;
- patrones de compra por segmento promocional;
- relación Boletin x Vale con probabilidades y conteos.

Las consultas SQL equivalentes se encuentran en [consultas_boletines_vales.sql](../database/consultas_boletines_vales.sql).
