import csv, sqlite3, os

DB = "data/superstore.db"
if os.path.exists(DB):
    os.remove(DB)
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.executescript("""
CREATE TABLE orders_raw (
    row_id INTEGER, order_id TEXT, order_date_raw TEXT, ship_date_raw TEXT,
    ship_mode TEXT, customer_id TEXT, customer_name TEXT, segment TEXT,
    country TEXT, city TEXT, state TEXT, postal_code TEXT, region TEXT,
    product_id TEXT, category TEXT, sub_category TEXT, product_name TEXT,
    sales REAL, quantity INTEGER, discount REAL, profit REAL
);
CREATE TABLE returns_raw (order_id TEXT, returned TEXT);
CREATE TABLE people_raw  (person TEXT, region TEXT);
""")

def num(cast):
    def f(v):
        v = v.strip()
        if v == "":
            return None          # real NULL, not a fake value
        try:
            return cast(v)
        except ValueError:
            return None
    return f

txt  = lambda v: v.strip() if v.strip() != "" else None
zip5 = lambda v: v.strip().zfill(5) if v.strip() else None   # restore lost leading zeros

def load(path, table, converters):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert len(header) == len(converters), (path, header)
        print(table, "header:", header)
        rows = [[c(v) for c, v in zip(converters, r)] for r in reader]
    cur.executemany(f"INSERT INTO {table} VALUES ({','.join('?'*len(converters))})", rows)
    print(table, len(rows), "rows loaded")

load("data/raw/orders.csv", "orders_raw",
     [num(int), txt, txt, txt, txt, txt, txt, txt, txt, txt, txt, zip5, txt,
      txt, txt, txt, txt, num(float), num(int), num(float), num(float)])
load("data/raw/returns.csv", "returns_raw", [txt, txt])
load("data/raw/people.csv",  "people_raw",  [txt, txt])

conn.commit(); conn.close()