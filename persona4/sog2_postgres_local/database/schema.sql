CREATE TABLE IF NOT EXISTS ventas_online (
    id_cliente   INTEGER PRIMARY KEY,
    edad         SMALLINT NOT NULL CHECK (edad BETWEEN 0 AND 120),
    genero       SMALLINT NOT NULL CHECK (genero IN (0, 1)),
    venta_total  NUMERIC(12, 3) NOT NULL CHECK (venta_total >= 0),
    n_compras    SMALLINT NOT NULL CHECK (n_compras >= 0),
    fecha_compra DATE NOT NULL,
    monto_compra NUMERIC(12, 3) NOT NULL CHECK (monto_compra >= 0),
    metodo_pago  SMALLINT NOT NULL CHECK (metodo_pago IN (0, 1, 2)),
    tiempo       INTEGER NOT NULL CHECK (tiempo >= 0),
    navegador    SMALLINT NOT NULL CHECK (navegador IN (0, 1, 2, 3, 4)),
    boletin      SMALLINT NOT NULL CHECK (boletin IN (0, 1)),
    vale         SMALLINT NOT NULL CHECK (vale IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_ventas_online_edad
    ON ventas_online (edad);

CREATE INDEX IF NOT EXISTS idx_ventas_online_fecha_compra
    ON ventas_online (fecha_compra);

CREATE INDEX IF NOT EXISTS idx_ventas_online_metodo_pago
    ON ventas_online (metodo_pago);

CREATE INDEX IF NOT EXISTS idx_ventas_online_navegador
    ON ventas_online (navegador);

CREATE OR REPLACE VIEW vw_ventas_online_legible AS
SELECT
    id_cliente,
    edad,
    CASE genero
        WHEN 1 THEN 'Femenino'
        WHEN 0 THEN 'Masculino'
    END AS genero,
    venta_total,
    n_compras,
    fecha_compra,
    monto_compra,
    CASE metodo_pago
        WHEN 0 THEN 'Efectivo'
        WHEN 1 THEN 'Tarjeta de Crédito'
        WHEN 2 THEN 'Tarjeta de Débito'
    END AS metodo_pago,
    tiempo,
    CASE navegador
        WHEN 0 THEN 'Tienda Física'
        WHEN 1 THEN 'Navegador 1'
        WHEN 2 THEN 'Navegador 2'
        WHEN 3 THEN 'Navegador 3'
        WHEN 4 THEN 'Navegador 4'
    END AS navegador,
    CASE boletin
        WHEN 1 THEN 'Sí'
        WHEN 0 THEN 'No'
    END AS boletin,
    CASE vale
        WHEN 1 THEN 'Sí'
        WHEN 0 THEN 'No'
    END AS vale
FROM ventas_online;
