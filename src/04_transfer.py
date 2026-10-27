import sqlite3
import pandas as pd

conn = sqlite3.connect("data/superstore.db")
df = pd.read_sql_query("SELECT * FROM orders_clean", conn,
                       parse_dates=["order_date", "ship_date"])

# --- Verification: pandas side must match SQL side ---
sql_rows   = conn.execute("SELECT COUNT(*) FROM orders_clean").fetchone()[0]
sql_sales  = conn.execute("SELECT SUM(sales) FROM orders_clean").fetchone()[0]
sql_profit = conn.execute("SELECT SUM(profit) FROM orders_clean").fetchone()[0]
sql_qty    = conn.execute("SELECT SUM(quantity) FROM orders_clean").fetchone()[0]
sql_ret    = conn.execute("SELECT SUM(is_returned) FROM orders_clean").fetchone()[0]

print("rows      :", len(df), "| SQL:", sql_rows)
print("sales     :", round(df.sales.sum(), 2), "| SQL:", round(sql_sales, 2))
print("profit    :", round(df.profit.sum(), 2), "| SQL:", round(sql_profit, 2))
print("quantity  :", df.quantity.sum(), "| SQL:", sql_qty)
print("returned  :", df.is_returned.sum(), "| SQL:", sql_ret)
print("\nnull counts per column (pandas):")
print(df.isna().sum()[df.isna().sum() > 0] if df.isna().sum().sum() else "none")
print("\ndtypes:\n", df.dtypes)

assert len(df) == sql_rows
assert abs(df.sales.sum() - sql_sales) < 1e-6
assert abs(df.profit.sum() - sql_profit) < 1e-6
assert df.quantity.sum() == sql_qty
assert df.is_returned.sum() == sql_ret
print("\nAll checks passed.")

df.to_pickle("data/clean.pkl")
conn.close()