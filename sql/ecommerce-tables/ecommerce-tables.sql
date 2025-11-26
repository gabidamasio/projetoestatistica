-- ******************************************************
-- DDL - CRIAÇÃO DE TABELAS
-- ******************************************************

CREATE TABLE dim_customer (
    id INTEGER PRIMARY KEY,
    customer_id VARCHAR(10),
    customer_name VARCHAR(100),
    city VARCHAR(100),
    state CHAR(2),
    region VARCHAR(20)
);

CREATE TABLE dim_delivery (
    id INTEGER PRIMARY KEY,
    delivery_id VARCHAR(10),
    services VARCHAR(20),
    p_sevice NUMERIC(10,2),
    d_forecast TIMESTAMP,
    d_date TIMESTAMP,
    status VARCHAR(20)
);


CREATE TABLE dim_products (
    id INTEGER PRIMARY KEY,
    product_id VARCHAR(10),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    price NUMERIC(10,2)
);


CREATE TABLE dim_shopping (
    id INTEGER PRIMARY KEY,
    shopping_id VARCHAR(10),
    address VARCHAR(200),
    city VARCHAR(100),
    state CHAR(2),
    cep VARCHAR(20)
);


CREATE TABLE fact_orders (
    id INTEGER PRIMARY KEY,
    order_date TIMESTAMP,
    discount NUMERIC(10,4),
    subtotal NUMERIC(10,2),
    total NUMERIC(10,2),
    payment VARCHAR(20),
    purchase_status VARCHAR(20)
);

ALTER TABLE fact_orders ADD COLUMN product_id VARCHAR(10);

UPDATE fact_orders
SET product_id = (
    SELECT dp.product_id
    FROM dim_products dp
    ORDER BY RANDOM()
    LIMIT 1
)
WHERE product_id IS NULL;

SELECT 
    COUNT(*) AS total_pedidos,
    COUNT(product_id) AS pedidos_com_product_id
FROM fact_orders;



-- ******************************************************
-- LIMPEZA DOS DADOS
-- Ajustar tipos
-- Remover duplicados
-- Tratar outliers
-- Verificar integridade
-- ******************************************************

-- ✅ AJUSTAR TIPOS (caso algum CSV tenha vindo errado)
ALTER TABLE fact_orders 
ALTER COLUMN discount TYPE NUMERIC(10,4),
ALTER COLUMN subtotal TYPE NUMERIC(10,2),
ALTER COLUMN total TYPE NUMERIC(10,2);

ALTER TABLE dim_delivery 
ALTER COLUMN p_sevice TYPE NUMERIC(10,2),
ALTER COLUMN d_forecast TYPE TIMESTAMP,
ALTER COLUMN d_date TYPE TIMESTAMP;

-- ✅ REMOVER DUPLICADOS (garantir unicidade por ID)
DELETE FROM fact_orders a
USING fact_orders b
WHERE a.ctid > b.ctid
  AND a.id = b.id;

DELETE FROM dim_delivery a
USING dim_delivery b
WHERE a.ctid > b.ctid
  AND a.id = b.id;

DELETE FROM dim_products a
USING dim_products b
WHERE a.ctid > b.ctid
  AND a.id = b.id;

-- ✅ TRATAMENTO DE NULLS CRÍTICOS
DELETE FROM fact_orders
WHERE order_date IS NULL
   OR total IS NULL;

-- ✅ TRATAMENTO DE OUTLIERS (IQR no total)
WITH stats AS (
    SELECT
        percentile_cont(0.25) WITHIN GROUP (ORDER BY total) AS q1,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY total) AS q3
    FROM fact_orders
)
DELETE FROM fact_orders
WHERE total < (SELECT q1 - 1.5 * (q3 - q1) FROM stats)
   OR total > (SELECT q3 + 1.5 * (q3 - q1) FROM stats);

-- ✅ VERIFICAR INTEGRIDADE REFERENCIAL (pedidos sem entrega)
DELETE FROM fact_orders fo
WHERE NOT EXISTS (
    SELECT 1 
    FROM dim_delivery dd 
    WHERE dd.id = fo.id
);

-- ✅ LIMPAR OS ESPACOS NOS IDS

UPDATE fact_orders
SET product_id = TRIM(product_id);

UPDATE dim_products
SET product_id = TRIM(product_id);




-- ******************************************************
-- DML / CRIACAO DAS COLUNAS DE KPIs
-- ******************************************************
-- indicadores dentro da tabela fact_orders para calcular os KPIs obrigatórios.

ALTER TABLE fact_orders ADD COLUMN IF NOT EXISTS discount_abs NUMERIC(10,2);
ALTER TABLE fact_orders ADD COLUMN IF NOT EXISTS is_confirmed INTEGER;
ALTER TABLE fact_orders ADD COLUMN IF NOT EXISTS delivery_delay INTEGER;
ALTER TABLE fact_orders ADD COLUMN IF NOT EXISTS delivery_lead_time INTEGER;
ALTER TABLE fact_orders ADD COLUMN IF NOT EXISTS is_late INTEGER;


-- discount_abs (valor absoluto do desconto)
UPDATE fact_orders SET discount_abs = discount * subtotal;

-- is_confirmed (se pagamento confirmado)
UPDATE fact_orders SET is_confirmed = CASE 
    WHEN purchase_status = 'Confirmado' THEN 1
    ELSE 0
END;

-- delivery_delay (atraso da entrega)
UPDATE fact_orders fo SET delivery_delay = (dd.d_date::date - dd.d_forecast::date)
FROM dim_delivery dd
WHERE fo.id = dd.id;

-- delivery_lead_time (tempo total até entrega)
UPDATE fact_orders fo SET delivery_lead_time = (dd.d_date::date - fo.order_date::date)
FROM dim_delivery dd
WHERE fo.id = dd.id;


-- is_late (se atrasou = 1, senão = 0) flag de atraso
UPDATE fact_orders fo SET is_late = CASE
                WHEN dd.d_date > dd.d_forecast THEN 1
                ELSE 0
              END
FROM dim_delivery dd
WHERE fo.id = dd.id;



-- ******************************************************
-- DML / VIEW GOLD
-- ******************************************************

DROP VIEW IF EXISTS vw_gold_orders;

CREATE VIEW vw_gold_orders AS
SELECT 
    -----------------------------------------
    -- 📌 Identificação do Pedido
    -----------------------------------------
    fo.id AS order_id,
    fo.order_date,
    fo.product_id,

    -----------------------------------------
    -- 🛒 KPIs Comerciais (fact_orders)
    -----------------------------------------
    fo.subtotal,
    fo.discount,
    fo.total,
    fo.payment,
    fo.purchase_status,

    -- Desconto absoluto (R$)
    (fo.discount * fo.subtotal) AS discount_abs,  
    
    -- Flag de pedido confirmado
    CASE 
        WHEN fo.purchase_status = 'Confirmado' THEN 1
        ELSE 0 
    END AS is_confirmed,

    -----------------------------------------
    -- 🚚 KPIs Logísticos (dim_delivery)
    -----------------------------------------
    dd.delivery_id,
    dd.services AS delivery_service,
    dd.p_sevice AS freight_price,       -- valor do frete
    dd.d_forecast AS delivery_forecast,
    dd.d_date AS delivery_date,
    dd.status AS delivery_status,

   -- Lead time real (nunca negativo)
	GREATEST(0, (dd.d_date::date - fo.order_date::date)) AS delivery_lead_time,
	
	-- Delay real (atraso nunca negativo)
	GREATEST(0, (dd.d_date::date - dd.d_forecast::date)) AS delivery_delay,
	
	-- Tempo estimado (nunca negativo)
	GREATEST(0, (dd.d_forecast::date - fo.order_date::date)) AS estimated_lead_time,


    -- Flag de atraso
    CASE 
        WHEN dd.d_date > dd.d_forecast THEN 1 
        ELSE 0 
    END AS is_late,

    -- Participação do frete % do total (proteção contra divisão por zero)
    (dd.p_sevice / NULLIF(fo.total,0)) AS freight_share,

    -----------------------------------------
    -- 🔄 KPIs Operacionais
    -----------------------------------------

    -- Flag pedido cancelado
    CASE WHEN fo.purchase_status = 'Cancelado' THEN 1
        ELSE 0
    END AS is_cancelled,

    -- Cancelamento por método de pagamento
    CONCAT(fo.payment, ' - ', fo.purchase_status) AS cancellation_by_payment,

    -----------------------------------------
    -- 📦 Informações do Produto (dim_products)
    -----------------------------------------
    dp.category,
    dp.subcategory,
    dp.price AS product_price

-----------------------------------------
FROM fact_orders fo

-- Ligação entre pedido e entrega
JOIN dim_delivery dd
      ON fo.id = dd.id        

-- Ligação correta entre pedido e produto
LEFT JOIN dim_products dp
      ON fo.product_id = dp.product_id;

 

-- Ver negativos nos tempos
SELECT 
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE delivery_lead_time < 0) AS negativos_lead_time,
    COUNT(*) FILTER (WHERE estimated_lead_time < 0) AS negativos_estimado,
    COUNT(*) FILTER (WHERE delivery_delay < 0) AS negativos_atraso
FROM vw_gold_orders;


-- . Conferir se categoria ainda está nula
SELECT 
    COUNT(*) AS total,
    COUNT(category) AS com_categoria,
    COUNT(*) - COUNT(category) AS sem_categoria
FROM vw_gold_orders;


-- Conferir consistência de datas
SELECT 
    MIN(order_date) AS menor_pedido,
    MIN(delivery_date) AS menor_entrega,
    MIN(delivery_forecast) AS menor_previsao
FROM vw_gold_orders