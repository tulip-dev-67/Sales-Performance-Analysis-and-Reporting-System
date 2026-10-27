DROP TABLE IF EXISTS orders_dates;
DROP TABLE IF EXISTS orders_dedup;
DROP TABLE IF EXISTS orders_std;
DROP TABLE IF EXISTS orders_clean;

-- 1. Convert DD-MM-YYYY text dates to real ISO dates (YYYY-MM-DD)
CREATE TABLE orders_dates AS
SELECT row_id, order_id, customer_id, customer_name, segment, country, city, state,
       postal_code, region, product_id, category, sub_category, product_name,
       sales, quantity, discount, profit, ship_mode,
       substr(order_date_raw,7,4)||'-'||substr(order_date_raw,4,2)||'-'||substr(order_date_raw,1,2) AS order_date,
       substr(ship_date_raw,7,4)||'-'||substr(ship_date_raw,4,2)||'-'||substr(ship_date_raw,1,2) AS ship_date
FROM orders_raw;

-- 2. Remove duplicates (unique line item = order_id + product_id + quantity)
CREATE TABLE orders_dedup AS
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id, product_id, quantity ORDER BY row_id) AS rn
  FROM orders_dates
) WHERE rn = 1;

-- 3. Standardize text and trim whitespace
CREATE TABLE orders_std AS
SELECT row_id, order_id, order_date, ship_date, customer_id, customer_name,
       UPPER(TRIM(segment)) AS segment, UPPER(TRIM(city)) AS city, UPPER(TRIM(state)) AS state,
       UPPER(TRIM(region)) AS region, product_id, UPPER(TRIM(category)) AS category,
       UPPER(TRIM(sub_category)) AS sub_category, product_name,
       sales, quantity, discount, profit,
       UPPER(TRIM(ship_mode)) AS ship_mode
FROM orders_dedup;

-- 4. Join Returns and People, create derived columns
CREATE TABLE orders_clean AS
WITH ret AS (SELECT DISTINCT order_id FROM returns_raw WHERE UPPER(TRIM(returned)) = 'YES'),
     ppl AS (SELECT DISTINCT UPPER(TRIM(region)) AS region, person FROM people_raw)
SELECT o.*,
  CASE WHEN r.order_id IS NOT NULL THEN 1 ELSE 0 END AS is_returned,
  p.person,
  CAST(strftime('%Y', o.order_date) AS INTEGER) AS order_year,
  CAST(strftime('%m', o.order_date) AS INTEGER) AS order_month,
  (CAST(strftime('%m', o.order_date) AS INTEGER) + 2) / 3 AS order_quarter,
  CASE WHEN o.quantity = 0 OR o.quantity IS NULL THEN NULL ELSE o.sales * 1.0 / o.quantity END AS unit_price,
  CASE WHEN o.sales = 0 OR o.sales IS NULL THEN NULL ELSE o.profit / o.sales END AS profit_margin,
  CAST(julianday(o.ship_date) - julianday(o.order_date) AS INTEGER) AS shipping_duration
FROM orders_std o
LEFT JOIN ret r ON o.order_id = r.order_id
LEFT JOIN ppl p ON o.region = p.region;