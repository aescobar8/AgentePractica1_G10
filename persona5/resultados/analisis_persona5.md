# Persona 5: género y comportamiento de compra

## Alcance

Esta sección analiza el uso de las columnas `Genero` y `N_Compras`, compara el comportamiento de compra entre géneros y examina su relación con el método de pago preferido. Cada fila representa un `Id_cliente` único.

## Validación y limpieza

- Fuente: tabla `ventas_online` en PostgreSQL, cargada desde `Venta_online_c.csv`.
- Registros analizados: 6,500.
- Valores nulos en `Genero`: 0.
- Valores nulos en `N_Compras`: 0.
- `Id_cliente` duplicados: 0.
- Dominio de `Genero`: solo se encontraron los valores 0 (Masculino) y 1 (Femenino), sin valores fuera de rango.
- Rango de `N_Compras`: mínimo 1, máximo 25, ambos consistentes con el resto de la distribución (sin outliers evidentes que sugieran error de captura).

No fue necesario descartar ni corregir registros: las 6,500 filas cumplieron las reglas de dominio y no se detectaron nulos ni duplicados.

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

La media (5.09) está por encima de la mediana (4.0), lo que indica una distribución con cola hacia la derecha: la mayoría de los clientes compra pocas veces (la moda es 2), pero un grupo menor de clientes con muchas compras (hasta 25) eleva el promedio.

Gráfica: [compras_por_genero.png](../graficas/compras_por_genero.png)

## Género y método de pago preferido

| Género | Efectivo | % | Tarjeta de Crédito | % | Tarjeta de Débito | % |
|---|---:|---:|---:|---:|---:|---:|
| Masculino | 601 | 17.82% | 2,021 | 59.93% | 750 | 22.24% |
| Femenino | 606 | 19.37% | 1,806 | 57.74% | 716 | 22.89% |

En ambos géneros la tarjeta de crédito es el método dominante, seguida de tarjeta de débito y por último efectivo. La diferencia entre géneros es pequeña pero consistente: los hombres usan tarjeta de crédito 2.2 puntos porcentuales más que las mujeres, y las mujeres usan efectivo 1.6 puntos porcentuales más que los hombres.

Gráfica: [metodo_pago_por_genero.png](../graficas/metodo_pago_por_genero.png)

## Conclusión

1. Se analizaron 6,500 registros de clientes correspondientes al CSV de ventas online de 2021, sin valores nulos ni duplicados en `Genero` ni `N_Compras`.
2. La base de clientes está compuesta por 3,372 hombres (51.88%) y 3,128 mujeres (48.12%), una diferencia de apenas 3.76 puntos porcentuales.
3. El promedio de compras (`N_Compras`) fue de 5.094 para hombres y 5.086 para mujeres, una diferencia de solo 0.008 compras en promedio.
4. En términos prácticos, el comportamiento de compra entre géneros es estadísticamente equivalente: no existe un género que compre notablemente más que el otro.
5. La moda global de `N_Compras` fue 2, lo que indica que el grupo más común de clientes realiza muy pocas compras durante el año.
6. La mediana de `N_Compras` fue 4.0, inferior a la media de 5.09, lo que confirma una distribución sesgada hacia la derecha.
7. El sesgo hacia la derecha ocurre porque un subconjunto de clientes de alta frecuencia (hasta 25 compras) eleva el promedio por encima de lo que compra la mayoría.
8. Este patrón de distribución (muchos clientes de baja frecuencia, pocos de alta frecuencia) se repite de forma casi idéntica entre hombres y mujeres, sin que el género explique la variación.
9. En método de pago, la tarjeta de crédito domina en ambos géneros: 59.93% en hombres y 57.74% en mujeres.
10. La tarjeta de débito ocupa el segundo lugar en ambos géneros, con porcentajes muy cercanos: 22.24% en hombres y 22.89% en mujeres.
11. El efectivo es el método menos usado en los dos grupos, con 17.82% en hombres y 19.37% en mujeres.
12. La diferencia más notable entre géneros aparece en el uso de tarjeta de crédito frente a efectivo: los hombres prefieren tarjeta de crédito 2.2 puntos porcentuales más que las mujeres, y las mujeres usan 1.6 puntos porcentuales más de efectivo que los hombres.
13. Aun así, esta diferencia es pequeña en magnitud absoluta (decenas de clientes sobre miles) y no representa un cambio de comportamiento estructural entre géneros.
14. La jerarquía de preferencia de pago (crédito > débito > efectivo) es idéntica para ambos géneros, solo cambian ligeramente las proporciones.
15. No se observó ninguna combinación de género y método de pago que fuera exclusiva o inusual: los seis cruces posibles (2 géneros x 3 métodos) están representados con cientos de clientes cada uno.
16. Estos resultados sugieren que, para esta empresa, el género no es un buen predictor del comportamiento de compra ni del método de pago preferido.
17. Esto contrasta con lo que suele asumirse en campañas de marketing tradicionales, donde se diseñan mensajes o promociones distintas según el género del cliente.
18. Dado que la variación entre géneros es mínima, los esfuerzos de personalización probablemente generen mejor retorno si se basan en otras variables (frecuencia de compra, edad, o uso de boletines/vales) en lugar del género.
19. La calidad de los datos en estas dos columnas fue alta desde el origen: no se requirió imputación de valores faltantes ni eliminación de registros inconsistentes, lo que da confianza en las conclusiones anteriores.
20. En conjunto, el género se comporta como una variable demográfica de bajo poder explicativo para esta empresa, y no debería ser el eje principal de la segmentación de clientes ni de las estrategias de pago.

## Recomendaciones

1. **No diseñar campañas ni promociones segmentadas únicamente por género.** Como el comportamiento de compra (`N_Compras`) y el método de pago preferido son prácticamente idénticos entre hombres y mujeres, invertir en creatividades o descuentos diferenciados por género tiene bajo retorno esperado. Es más eficiente reasignar ese presupuesto a segmentar por frecuencia de compra (por ejemplo, distinguiendo el grupo de moda 2 compras/año de los clientes de alta frecuencia) o por otras variables del análisis del equipo (edad, uso de boletín/vale).
2. **Incentivar el pago con tarjeta de crédito y débito por encima del efectivo, sin diferenciar por género.** Dado que ambos géneros ya prefieren fuertemente las tarjetas (más del 80% de los clientes de cada género paga con crédito o débito), la empresa puede negociar mejores condiciones con los procesadores de pago o lanzar promociones de cashback/puntos ligadas a tarjeta, aplicables a toda la base de clientes por igual, sin necesidad de crear variantes por género.

## Pregunta E: ¿Implementar un Chat conversacional de IA afectaría a la empresa para que entregue el análisis de los datos a futuro?

Sí, y el efecto sería positivo siempre que el chat se mantenga como una capa de consulta sobre datos ya validados, no como sustituto del análisis humano. Para esta parte del proyecto (género y comportamiento de compra), un chat conectado al MCP Server permite que cualquier persona de la empresa —no solo el equipo de analistas— pregunte directamente "¿qué método de pago prefieren las mujeres?" o "¿compran más los hombres que las mujeres?" y reciba una respuesta con los números exactos de la base de datos en segundos, en lugar de esperar un informe estático. Esto reduce el tiempo entre pregunta de negocio y respuesta accionable, y democratiza el acceso al análisis dentro de la organización. El riesgo principal es que el chat entregue una respuesta sin el contexto estadístico correcto (por ejemplo, reportar que "los hombres compran más" sin aclarar que la diferencia es de 0.008 compras y no es significativa); por eso las funciones expuestas al MCP deben devolver también los denominadores y porcentajes, no solo el número ganador, para que el modelo de lenguaje no sobreinterprete diferencias pequeñas como si fueran tendencias fuertes. Con esa salvedad, sí conviene implementarlo a futuro: mantiene el análisis actualizado automáticamente cada vez que se cargan datos nuevos, sin depender de que un analista regenere manualmente el informe.
