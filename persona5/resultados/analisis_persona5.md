# Persona 5: género y comportamiento de compra

## Alcance

Esta sección analiza las columnas `Genero` y `N_Compras`, compara el comportamiento de compra entre géneros y revisa su relación con el método de pago preferido. Cada fila representa un `Id_cliente` único.

## Validación y limpieza

- Fuente: tabla `ventas_online` en PostgreSQL, cargada desde `Venta_online_c.csv`.
- Registros analizados: 6,500.
- Valores nulos en `Genero`: 0.
- Valores nulos en `N_Compras`: 0.
- `Id_cliente` duplicados: 0.
- Dominio de `Genero`: solo aparecen los valores 0 (Masculino) y 1 (Femenino).
- Rango de `N_Compras`: de 1 a 25, sin valores que rompan con el resto de la distribución.

Las 6,500 filas cumplieron las reglas de dominio, así que no hubo que descartar ni corregir ningún registro.

## Resumen general por género

| Género | Clientes | % del total | Total de compras (suma de N_Compras) | Compras promedio |
|---|---:|---:|---:|---:|
| Masculino | 3,372 | 51.88% | 17,176 | 5.094 |
| Femenino | 3,128 | 48.12% | 15,909 | 5.086 |

## Estadísticas de N_Compras

| Indicador | Global | Masculino | Femenino |
|---|---:|---:|---:|
| Media | 5.09 | 5.094 | 5.086 |
| Mediana | 4.0 | — | — |
| Moda | 2 | — | — |

La media (5.09) queda por encima de la mediana (4.0), lo que apunta a una distribución con cola hacia la derecha: la mayoría de los clientes compra pocas veces (la moda es 2), y un grupo más chico de clientes con muchas compras, hasta 25, empuja el promedio hacia arriba.

Gráfica: [compras_por_genero.png](../graficas/compras_por_genero.png)

## Género y método de pago preferido

| Género | Efectivo | % | Tarjeta de Crédito | % | Tarjeta de Débito | % |
|---|---:|---:|---:|---:|---:|---:|
| Masculino | 601 | 17.82% | 2,021 | 59.93% | 750 | 22.24% |
| Femenino | 606 | 19.37% | 1,806 | 57.74% | 716 | 22.89% |

En ambos géneros domina la tarjeta de crédito, seguida de la de débito y por último el efectivo. La diferencia entre géneros es chica pero se repite en la misma dirección: los hombres usan tarjeta de crédito 2.2 puntos porcentuales más que las mujeres, y las mujeres pagan en efectivo 1.6 puntos porcentuales más que los hombres.

Gráfica: [metodo_pago_por_genero.png](../graficas/metodo_pago_por_genero.png)

## Conclusión

El análisis de los 6,500 registros de ventas online de 2021 muestra que el género aporta muy poco para explicar el comportamiento de compra de los clientes de esta empresa. La base está bastante pareja entre los dos grupos, con 3,372 hombres (51.88%) y 3,128 mujeres (48.12%), una diferencia de solo 3.76 puntos porcentuales que no sugiere ningún sesgo relevante en quién compra en la tienda. Estos números salieron de datos limpios desde el origen: no hubo nulos ni duplicados en `Genero` ni en `N_Compras`, así que no hace falta descontar ningún problema de calidad al leer estas conclusiones.

Al mirar `N_Compras`, el número de compras que hace cada cliente, el promedio es prácticamente igual entre géneros: 5.094 para hombres y 5.086 para mujeres, una diferencia de 0.008 compras que no tiene ningún peso práctico. Esa diferencia es tan chica que, en los hechos, hombres y mujeres compran igual, y no hay un género que compre notablemente más que el otro. Los dos grupos siguen además la misma forma de distribución: la moda global es 2 (el grupo más común de clientes compra muy pocas veces al año), la mediana es 4.0 y la media sube a 5.09 porque un grupo más chico de clientes de alta frecuencia, con hasta 25 compras, jala el promedio hacia arriba. Esa combinación de moda baja, mediana intermedia y media más alta describe una distribución con cola hacia la derecha que se repite casi igual en hombres y mujeres, sin que el género marque ninguna diferencia real.

En método de pago pasa algo parecido. La tarjeta de crédito domina en los dos géneros (59.93% en hombres, 57.74% en mujeres), seguida de la tarjeta de débito (22.24% en hombres, 22.89% en mujeres) y por último el efectivo (17.82% en hombres, 19.37% en mujeres). El orden de preferencia es idéntico entre géneros, y lo único que cambia son las proporciones: los hombres prefieren tarjeta de crédito 2.2 puntos porcentuales más que las mujeres, y las mujeres usan efectivo 1.6 puntos porcentuales más que los hombres. Ninguno de los seis cruces posibles entre género y método de pago quedó vacío o con un comportamiento raro, todos tienen cientos de clientes, y esa diferencia de un par de puntos porcentuales no marca un cambio real de comportamiento entre los dos grupos.

Con estos números, el género no funciona como buen predictor ni del comportamiento de compra ni del método de pago que usa un cliente en esta empresa, algo que va en contra de lo que suelen asumir las campañas de marketing tradicionales, armadas con mensajes o promociones distintas según el género del cliente. Si la diferencia entre géneros es tan chica, tiene más sentido personalizar por otras variables donde sí puede haber diferencias que valga la pena explotar, como la frecuencia de compra, la edad o el uso de boletines y vales que analizó el resto del equipo. En esta empresa, en resumen, el género no debería ser el eje principal para segmentar clientes ni para decidir estrategias de pago.

## Recomendaciones

1. No armar campañas ni promociones separadas por género. El comportamiento de compra y el método de pago preferido son casi idénticos entre hombres y mujeres, así que invertir en creatividades o descuentos diferenciados por género rinde poco. Ese presupuesto se aprovecha mejor segmentando por frecuencia de compra (por ejemplo, separando al grupo que compra 2 veces al año de los clientes de alta frecuencia) o por las otras variables que analizó el equipo, como edad o uso de boletín y vale.
2. Impulsar el pago con tarjeta, crédito y débito, por encima del efectivo, sin diferenciar por género. Como ambos géneros ya prefieren fuerte las tarjetas (más del 80% de cada grupo paga con crédito o débito), la empresa puede negociar mejores condiciones con los procesadores de pago o lanzar promociones de cashback o puntos ligadas a tarjeta, aplicables a toda la base de clientes por igual.

## Pregunta E: ¿Implementar un Chat conversacional de IA afectaría a la empresa para que entregue el análisis de los datos a futuro?

Sí, y de forma positiva, siempre que el chat se quede como una capa de consulta sobre datos ya validados y no reemplace el análisis humano. Para esta parte del proyecto, un chat conectado al MCP Server permite que cualquier persona de la empresa, no solo el equipo de analistas, pregunte directamente "¿qué método de pago prefieren las mujeres?" o "¿compran más los hombres que las mujeres?" y reciba la respuesta con los números exactos de la base de datos en segundos, en vez de esperar un informe estático. Eso reduce el tiempo entre una pregunta de negocio y una respuesta útil. El riesgo principal es que el chat responda sin el contexto estadístico correcto, por ejemplo diciendo que "los hombres compran más" sin aclarar que la diferencia real es de 0.008 compras y no significa nada. Por eso las funciones que se conecten al MCP deben devolver también los denominadores y porcentajes, no solo el número más alto, para que el modelo no le dé demasiado peso a diferencias chicas. Con ese cuidado, sí vale la pena implementarlo: mantiene el análisis actualizado cada vez que se cargan datos nuevos, sin que un analista tenga que rehacer el informe a mano.
