import sqlite3

conn = sqlite3.connect("data/superstore.db")
conn.executescript(open("sql/03_clean.sql").read())
conn.commit()

q = lambda s: conn.execute(s).fetchall()
print("rows: raw", q("SELECT COUNT(*) FROM orders_raw")[0][0],
      "| after dedup", q("SELECT COUNT(*) FROM orders_dedup")[0][0],
      "| final", q("SELECT COUNT(*) FROM orders_clean")[0][0])
print("returned line items / orders:", q("SELECT COUNT(*), COUNT(DISTINCT order_id) FROM orders_clean WHERE is_returned = 1")[0])
print("rows with no person:", q("SELECT COUNT(*) FROM orders_clean WHERE person IS NULL")[0][0])
print("date range:", q("SELECT MIN(order_date), MAX(order_date) FROM orders_clean")[0])
print("shipping_duration min/max:", q("SELECT MIN(shipping_duration), MAX(shipping_duration) FROM orders_clean")[0])
conn.close()