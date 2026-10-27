import sqlite3

conn = sqlite3.connect("data/superstore.db")
cur = conn.cursor()

def show(title, sql):
    print(f"\n--- {title}")
    rows = cur.execute(sql).fetchall()
    for r in rows:
        print(r)
    if not rows:
        print("(none)")

# 1. Null count per column, for every table (before changing anything)
for table in ["orders_raw", "returns_raw", "people_raw"]:
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({table})")]
    sql = "SELECT " + ", ".join(f"SUM({c} IS NULL)" for c in cols) + f" FROM {table}"
    counts = cur.execute(sql).fetchone()
    print(f"\n--- null counts: {table}")
    for c, n in zip(cols, counts):
        print(f"{c:18} {n}")

# 2. Duplicates
show("duplicate line items in orders (order_id + product_id + quantity)",
     "SELECT order_id, product_id, quantity, COUNT(*) FROM orders_raw GROUP BY 1,2,3 HAVING COUNT(*) > 1")
show("duplicate order_id in returns",
     "SELECT order_id, COUNT(*) FROM returns_raw GROUP BY 1 HAVING COUNT(*) > 1")
show("regions with more than one person in people",
     "SELECT region, COUNT(*) FROM people_raw GROUP BY 1 HAVING COUNT(*) > 1")

# 3. Date format check
show("order_date_raw lengths", "SELECT LENGTH(order_date_raw), COUNT(*) FROM orders_raw GROUP BY 1")
show("ship_date_raw lengths", "SELECT LENGTH(ship_date_raw), COUNT(*) FROM orders_raw GROUP BY 1")

# 4. Baseline distribution of numeric columns (min, avg, max)
for col in ["sales", "quantity", "discount", "profit"]:
    show(f"{col}: min, avg, max", f"SELECT MIN({col}), ROUND(AVG({col}),4), MAX({col}) FROM orders_raw")

# 5. Text columns
show("ship_mode values", "SELECT ship_mode, COUNT(*) FROM orders_raw GROUP BY 1")
show("region values", "SELECT region, COUNT(*) FROM orders_raw GROUP BY 1")
show("returned values", "SELECT returned, COUNT(*) FROM returns_raw GROUP BY 1")