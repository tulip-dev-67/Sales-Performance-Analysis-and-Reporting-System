import matplotlib
matplotlib.use("Agg")          # save files only, no pop-up windows
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_pickle("data/clean.pkl")
OUT = "outputs/charts/"
N = 10

def save(name):
    plt.tight_layout()
    plt.savefig(OUT + name, dpi=150, bbox_inches="tight")
    plt.close()
    print("saved", name)

# 1. Bar: total sales by state (top 15)
s = df.groupby("state").sales.sum().nlargest(15).sort_values()
plt.figure(figsize=(9, 6))
plt.barh(s.index, s.values, color="#2E75B6")
plt.title("Total sales by state (top 15)"); plt.xlabel("Sales")
save("01_sales_by_state.png")

# 2. Bar: total sales by category
c = df.groupby("category").sales.sum().sort_values(ascending=False)
plt.figure(figsize=(7, 5))
plt.bar(c.index, c.values, color="#2E75B6")
plt.title("Total sales by category"); plt.ylabel("Sales")
plt.xticks(rotation=15)
save("02_sales_by_category.png")

# 3. Line: sales over time (monthly)
m = df.groupby(df.order_date.dt.to_period("M")).sales.sum()
m.index = m.index.to_timestamp()
plt.figure(figsize=(10, 5))
plt.plot(m.index, m.values, marker="o", color="#2E75B6")
plt.title("Monthly sales over time"); plt.ylabel("Sales"); plt.grid(alpha=0.3)
save("03_sales_over_time.png")

# 4. Pie: share of sales by region
r = df.groupby("region").sales.sum()
plt.figure(figsize=(6, 6))
plt.pie(r.values, labels=r.index, autopct="%1.1f%%", startangle=90)
plt.title("Share of sales by region")
save("04_sales_by_region_pie.png")

# 5. Bar: top N products by sales
p = df.groupby("product_name").sales.sum().nlargest(N).sort_values()
labels = [n if len(n) <= 45 else n[:42] + "..." for n in p.index]
plt.figure(figsize=(10, 6))
plt.barh(labels, p.values, color="#2E75B6")
plt.title(f"Top {N} products by sales"); plt.xlabel("Sales")
save("05_top_products.png")

# 6. Scatter: discount vs profit margin (+ average margin per discount level)
plt.figure(figsize=(9, 6))
plt.scatter(df.discount * 100, df.profit_margin * 100, alpha=0.15, s=12, color="#7F7F7F")
avg = df.groupby("discount").profit_margin.mean()
plt.plot(avg.index * 100, avg.values * 100, color="#C00000", marker="o", label="Average margin")
plt.axhline(0, color="black", linewidth=1)
plt.title("Discount vs profit margin"); plt.xlabel("Discount (%)"); plt.ylabel("Profit margin (%)")
plt.legend()
save("06_discount_vs_margin.png")