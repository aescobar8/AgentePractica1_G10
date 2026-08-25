-- Consultas de la persona 5.
-- Todas las consultas usan la tabla ventas_online definida en schema.sql.

-- 1. Resumen de comportamiento de compra por género.
SELECT
    CASE genero WHEN 1 THEN 'Femenino' WHEN 0 THEN 'Masculino' END AS genero,
    COUNT(*) AS total_clientes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje_clientes,
    SUM(n_compras) AS total_compras,
    ROUND(AVG(n_compras), 3) AS compras_media
FROM ventas_online
GROUP BY genero
ORDER BY genero;

-- 2. Media, mediana y moda de N_Compras (global).
SELECT
    ROUND(AVG(n_compras), 3) AS media,
    (PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY n_compras))::NUMERIC AS mediana,
    MODE() WITHIN GROUP (ORDER BY n_compras) AS moda
FROM ventas_online;

-- 3. Relación entre género y método de pago preferido.
SELECT
    CASE genero WHEN 1 THEN 'Femenino' WHEN 0 THEN 'Masculino' END AS genero,
    CASE metodo_pago
        WHEN 0 THEN 'Efectivo'
        WHEN 1 THEN 'Tarjeta de Crédito'
        WHEN 2 THEN 'Tarjeta de Débito'
    END AS metodo_pago,
    COUNT(*) AS clientes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY genero), 2) AS porcentaje_dentro_genero
FROM ventas_online
GROUP BY genero, metodo_pago
ORDER BY genero, metodo_pago;
