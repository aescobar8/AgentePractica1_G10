-- Consultas de la persona 6.
-- Todas las consultas usan la tabla ventas_online definida en schema.sql.

-- 1. Resumen general de uso de boletines y vales.
SELECT
    COUNT(*) AS total_clientes,
    SUM(boletin) AS clientes_con_boletin,
    ROUND(100.0 * SUM(boletin) / NULLIF(COUNT(*), 0), 2) AS porcentaje_boletin,
    SUM(vale) AS clientes_con_vale,
    ROUND(100.0 * SUM(vale) / NULLIF(COUNT(*), 0), 2) AS porcentaje_vale,
    SUM(CASE WHEN boletin = 1 AND vale = 1 THEN 1 ELSE 0 END) AS clientes_con_ambos,
    SUM(CASE WHEN boletin = 0 AND vale = 0 THEN 1 ELSE 0 END) AS clientes_sin_promocion
FROM ventas_online;

-- 2. Uso mensual de boletines y vales.
SELECT
    EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes_num,
    TO_CHAR(DATE_TRUNC('month', fecha_compra), 'YYYY-MM') AS mes,
    COUNT(*) AS registros,
    SUM(boletin) AS boletines_usados,
    ROUND(100.0 * SUM(boletin) / NULLIF(COUNT(*), 0), 2) AS porcentaje_boletines,
    SUM(vale) AS vales_usados,
    ROUND(100.0 * SUM(vale) / NULLIF(COUNT(*), 0), 2) AS porcentaje_vales
FROM ventas_online
WHERE EXTRACT(YEAR FROM fecha_compra) = 2021
GROUP BY mes_num, mes
ORDER BY mes_num;

-- 3. Patrones de compra por segmento promocional.
SELECT
    CASE
        WHEN boletin = 1 AND vale = 1 THEN 'Ambos'
        WHEN boletin = 1 AND vale = 0 THEN 'Solo boletin'
        WHEN boletin = 0 AND vale = 1 THEN 'Solo vale'
        ELSE 'Ninguno'
    END AS segmento,
    COUNT(*) AS registros,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje_registros,
    ROUND(AVG(venta_total), 3) AS venta_total_media,
    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY venta_total))::NUMERIC, 3) AS venta_total_mediana,
    ROUND(AVG(n_compras), 3) AS compras_media,
    ROUND(AVG(monto_compra), 3) AS monto_compra_media
FROM ventas_online
GROUP BY segmento
ORDER BY CASE segmento
    WHEN 'Ninguno' THEN 1
    WHEN 'Solo boletin' THEN 2
    WHEN 'Solo vale' THEN 3
    WHEN 'Ambos' THEN 4
END;

-- 4. Tabla de contingencia Boletin x Vale.
SELECT
    boletin,
    vale,
    COUNT(*) AS registros,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje_total
FROM ventas_online
GROUP BY boletin, vale
ORDER BY boletin, vale;

-- 5. Probabilidades condicionales para evaluar la relación entre promociones.
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN boletin = 1 AND vale = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN boletin = 1 THEN 1 ELSE 0 END), 0),
        2
    ) AS porcentaje_vale_dado_boletin,
    ROUND(
        100.0 * SUM(CASE WHEN boletin = 0 AND vale = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN boletin = 0 THEN 1 ELSE 0 END), 0),
        2
    ) AS porcentaje_vale_sin_boletin,
    CORR(boletin::NUMERIC, vale::NUMERIC) AS correlacion_phi
FROM ventas_online;

-- 6. Meses prioritarios para campañas.
WITH uso_mensual AS (
    SELECT
        EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes_num,
        SUM(boletin) AS boletines_usados,
        SUM(vale) AS vales_usados
    FROM ventas_online
    WHERE EXTRACT(YEAR FROM fecha_compra) = 2021
    GROUP BY mes_num
)
SELECT
    mes_num,
    boletines_usados,
    vales_usados,
    RANK() OVER (ORDER BY boletines_usados DESC) AS posicion_boletines,
    RANK() OVER (ORDER BY vales_usados DESC) AS posicion_vales
FROM uso_mensual
ORDER BY mes_num;
