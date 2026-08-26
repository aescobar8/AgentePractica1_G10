-- Consultas equivalentes al análisis de Persona 1.

-- Ventas totales y estadísticas generales.
SELECT COUNT(*) AS registros,
       ROUND(SUM(venta_total), 3) AS ventas_totales,
       ROUND(AVG(venta_total), 3) AS media,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY venta_total) AS mediana,
       MODE() WITHIN GROUP (ORDER BY venta_total) AS moda,
       MIN(venta_total) AS minimo,
       MAX(venta_total) AS maximo
FROM ventas_online;

-- Distribución de ventas por mes.
SELECT EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes_num,
       TO_CHAR(DATE_TRUNC('month', fecha_compra), 'TMMonth') AS mes,
       COUNT(*) AS registros,
       ROUND(SUM(venta_total), 3) AS ventas_totales,
       ROUND(AVG(venta_total), 3) AS venta_media,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY venta_total) AS venta_mediana,
       MODE() WITHIN GROUP (ORDER BY venta_total) AS venta_moda
FROM ventas_online
WHERE EXTRACT(YEAR FROM fecha_compra) = 2021
GROUP BY mes_num, mes
ORDER BY mes_num;
