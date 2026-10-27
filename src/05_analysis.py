import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

df = pd.read_pickle("data/clean.pkl")
N = 10
report = []

def out(title, obj=""):
    text = f"\n=== {title} ===\n{obj}"
    print(text)
    report.append(text)

# ---------- 1. Sales performance metrics ----------
# Sales is already the line total after discount, so we never multiply by Quantity.
total_sales, total_qty, total_profit = df.sales.sum(), df.quantity.sum(), df.profit.sum()
order_sales = df.groupby("order_id").sales.sum()        # line items -> order level first
out("1. Overall metrics", pd.Series({
    "total_sales": total_sales, "total_quantity": total_qty, "total_profit": total_profit,
    "avg_sales_per_order": order_sales.mean(), "overall_profit_margin": total_profit / total_sales}))

# ---------- 2. Top performers ----------
out(f"2a. Top {N} products by sales", df.groupby("product_name").sales.sum().nlargest(N))
out(f"2b. Top {N} products by quantity", df.groupby("product_name").quantity.sum().nlargest(N))
out(f"2c. Top {N} customers by sales",
    df.groupby(["customer_id", "customer_name"]).sales.sum().nlargest(N))

# ---------- 3. Geography ----------
state = df.groupby("state")[["sales", "profit"]].sum().sort_values("sales", ascending=False)
city = df.groupby("city")[["sales", "profit"]].sum().sort_values("sales", ascending=False)
region = df.groupby("region")[["sales", "profit"]].sum().sort_values("sales", ascending=False)
out("3a. Sales and profit by state (top 15)", state.head(15))
out("3b. Sales and profit by city (top 15)", city.head(15))
out("3c. Sales and profit by region", region)

hi_neg = state[(state.sales > state.sales.median()) & (state.profit < 0)]
out("3d. States with above-median sales but negative profit", hi_neg)
if len(hi_neg):
    sub = df[df.state.isin(hi_neg.index)]
    out("3e. Driver check: average discount in those states vs overall",
        pd.Series({"flagged_states_avg_discount": sub.discount.mean(),
                   "overall_avg_discount": df.discount.mean()}))
    out("3f. Driver check: profit by sub-category in those states (worst 8)",
        sub.groupby("sub_category").profit.sum().nsmallest(8))

# ---------- 4. Category and sub-category ----------
out("4a. Category: sales and quantity", df.groupby("category")[["sales", "quantity"]].sum())
out("4b. Sub-category: sales and quantity",
    df.groupby("sub_category")[["sales", "quantity"]].sum().sort_values("sales", ascending=False))

# ---------- 5. Sales representatives ----------
out("5a. Sales and profit per person", df.groupby("person")[["sales", "profit"]].sum())
out("5b. Sales and quantity per category per person",
    df.pivot_table(index="person", columns="category", values=["sales", "quantity"], aggfunc="sum"))

# ---------- 6. Returns (order level) ----------
orders = df.groupby("order_id").agg(returned=("is_returned", "max"))
out("6a. Returns", pd.Series({
    "total_orders": len(orders), "returned_orders": int(orders.returned.sum()),
    "return_rate": orders.returned.mean()}))

def return_rate_by(col):
    # per group: distinct orders containing it, and how many of those were returned
    t = df.groupby(col).agg(orders=("order_id", "nunique"))
    t["returned_orders"] = df[df.is_returned == 1].groupby(col).order_id.nunique()
    t["returned_orders"] = t.returned_orders.fillna(0)
    t["return_rate"] = t.returned_orders / t.orders
    return t

out("6b. Return rate by category", return_rate_by("category").sort_values("return_rate", ascending=False))
out("6c. Return rate by sub-category (top 8)",
    return_rate_by("sub_category").sort_values("return_rate", ascending=False).head(8))

# ---------- 7. Region x Segment ----------
# one row per order, so each customer segment is counted once per order
ord1 = df.drop_duplicates("order_id")
mix = pd.crosstab(ord1.region, ord1.segment, normalize="index") * 100
overall_mix = ord1.segment.value_counts(normalize=True) * 100
out("7a. Region x Segment counts (orders)", pd.crosstab(ord1.region, ord1.segment))
out("7b. Segment mix per region (%)", mix)
out("7c. Overall segment mix (%)", overall_mix)
out("7d. Difference from overall mix (percentage points)", mix - overall_mix)

# ---------- 8. Product performance and shipping ----------
prod = df.groupby("product_id").agg(
    product_name=("product_name", "first"), sales=("sales", "sum"),
    quantity=("quantity", "sum"), profit=("profit", "sum"),
    n_orders=("order_id", "nunique"))
prod["returned_orders"] = df[df.is_returned == 1].groupby("product_id").order_id.nunique()
prod["returned_orders"] = prod.returned_orders.fillna(0)
prod["return_rate"] = prod.returned_orders / prod.n_orders
prod["adj_profit"] = prod.profit * (1 - prod.return_rate)
prod["adj_margin"] = prod.adj_profit / prod.sales
out("8a. Product metrics (first 5 rows)", prod.head())

# Underperformers: only products with enough orders to be meaningful
enough = prod[prod.n_orders >= 10]
bad = enough[(enough.return_rate >= enough.return_rate.quantile(0.9)) |
             (enough.adj_margin <= enough.adj_margin.quantile(0.1))]
out("8b. Underperforming products (>=10 orders; top-10% return rate or bottom-10% adj margin)",
    bad.sort_values("adj_margin")[["product_name", "n_orders", "return_rate", "adj_profit", "adj_margin"]].head(15))

stats = lambda col: df.groupby(col).shipping_duration.agg(["mean", "median", "std"])
out("8c. Shipping duration by ship mode", stats("ship_mode"))
out("8d. Shipping duration by region", stats("region"))

out("8e. Return rate by ship mode", return_rate_by("ship_mode"))
out("8f. Return rate by region", return_rate_by("region"))

bins = [-0.001, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
labels = ["0%", "0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50%+"]
df["discount_band"] = pd.cut(df.discount, bins=bins, labels=labels)
lvl = df.groupby("discount_band", observed=True).agg(
    lines=("row_id", "count"), quantity=("quantity", "sum"),
    sales=("sales", "sum"), profit=("profit", "sum"))
lvl["margin"] = lvl.profit / lvl.sales
out("8g/8h. Sales, profit and margin by discount band", lvl)

with open("outputs/analysis_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print("\nSaved to outputs/analysis_results.txt")