import pymysql
import random
from datetime import datetime, timedelta

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Leecamtus@123',
    database='restaurant_db',
    charset='utf8mb4'
)
cursor = conn.cursor()
print("Inserting sample data...")

# ── 1. CUSTOMERS (100 rows) ──────────────────────────────
first_names = ['James','John','Robert','Michael','William','David','Joseph','Charles',
               'Thomas','Daniel','Emma','Olivia','Sophia','Isabella','Mia','Charlotte',
               'Amelia','Harper','Evelyn','Abigail','Emily','Elizabeth','Sofia','Avery',
               'Ella','Madison','Scarlett','Victoria','Aria','Grace']
last_names  = ['Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis',
               'Wilson','Anderson','Taylor','Thomas','Jackson','White','Harris','Martin',
               'Thompson','Young','Allen','King','Wright','Scott','Hill','Green','Adams']

streets   = ['Oak Street','Maple Avenue','Cedar Lane','Pine Road','Elm Street',
             'Washington Blvd','Lincoln Ave','Park Place','River Road','Lake Drive']
districts = ['District 1','District 3','District 5','District 7','District 10',
             'Binh Thanh','Go Vap','Tan Binh','Thu Duc','Phu Nhuan']

customers, phones_used = [], set()
for _ in range(100):
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    while True:
        phone = f"0{random.randint(3,9)}{random.randint(10000000,99999999)}"
        if phone not in phones_used:
            phones_used.add(phone)
            break
    address = f"{random.randint(1,200)} {random.choice(streets)}, {random.choice(districts)}"
    customers.append((name, phone, address))

cursor.executemany(
    "INSERT INTO Customers (CustomerName, PhoneNumber, Address) VALUES (%s,%s,%s)",
    customers
)
conn.commit()
print(f"✅ Inserted {len(customers)} customers")

# ── 2. TABLES (20 rows) ───────────────────────────────────
tables = [(i, random.choice(['available','available','available','reserved']))
          for i in range(1, 21)]
cursor.executemany(
    "INSERT INTO Tables (TableNumber, Status) VALUES (%s,%s)",
    tables
)
conn.commit()
print(f"✅ Inserted {len(tables)} tables")

# ── 3. MENUITEMS (15 rows) ────────────────────────────────
menu_items = [
    ('Spaghetti Carbonara',    185000, 'Entree',   'spaghetti_carbonara.jpg'),
    ('Fettuccine Alfredo',     175000, 'Entree',   'fettuccine_alfredo.jpg'),
    ('Penne Arrabiata',        165000, 'Entree',   'penne_arrabiata.jpg'),
    ('Lasagne Bolognese',      195000, 'Entree',   'lasagne_bolognese.jpg'),
    ('Mushroom Risotto',       220000, 'Entree',   'mushroom_risotto.jpg'),
    ('Beef Steak',             350000, 'Main',     'beef_steak.jpg'),
    ('Herb Roasted Chicken',   245000, 'Main',     'herb_roasted_chicken.jpg'),
    ('Grilled Salmon',         290000, 'Main',     'grilled_salmon.jpg'),
    ('Pizza Margherita',       175000, 'Pizza',    'pizza_margherita.jpg'),
    ('Cream of Mushroom Soup',  75000, 'Starter',  'cream_of_mushroom_soup.jpg'),
    ('Caesar Salad',            95000, 'Starter',  'caesar_salad.jpg'),
    ('Garlic Bread',            45000, 'Starter',  'garlic_bread.jpg'),
    ('Tiramisu',                85000, 'Dessert',  'tiramisu.jpg'),
    ('Panna Cotta',             75000, 'Dessert',  'panna_cotta.jpg'),
    ('Cappuccino',              65000, 'Beverage', 'cappuccino.jpg'),
]
cursor.executemany(
    "INSERT INTO MenuItems (DishName, Price, Category, Available, ImageFilename) VALUES (%s,%s,%s,%s,%s)",
    [(n, p, c, True, img) for n, p, c, img in menu_items]
)
conn.commit()
print(f"✅ Inserted {len(menu_items)} menu items")

# ── 4. RESERVATIONS (100 rows) ────────────────────────────
now = datetime.now()
reservations = []
for _ in range(100):
    cid    = random.randint(1, 100)
    tid    = random.randint(1, 20)
    offset = random.randint(-60, 30)
    dt     = now + timedelta(days=offset,
                             hours=random.randint(-now.hour, 23-now.hour),
                             minutes=random.choice([0, 15, 30, 45]))
    guests = random.randint(1, 8)
    status = random.choices(['confirmed','cancelled'], weights=[70, 30])[0]
    reservations.append((cid, tid, dt.strftime('%Y-%m-%d %H:%M:%S'), guests, status))

cursor.executemany(
    "INSERT INTO Reservations (CustomerID,TableID,DateTime,GuestCount,Status) VALUES (%s,%s,%s,%s,%s)",
    reservations
)
conn.commit()
print(f"✅ Inserted {len(reservations)} reservations")

# ── 5. INVOICES + INVOICE DETAILS (300 rows) ─────────────
# Date range: Jan 1, 2026 → May 13, 2026
start_date = datetime(2026, 1, 1)
end_date   = datetime(2026, 5, 13)
date_range = (end_date - start_date).days

for _ in range(300):
    cid    = random.randint(1, 100)
    tid    = random.randint(1, 20)
    pdate  = start_date + timedelta(
                days=random.randint(0, date_range),
                hours=random.randint(10, 22)
             )
    method = random.choice(['cash', 'card'])

    cursor.execute(
        "INSERT INTO Invoices (CustomerID,TableID,TotalAmount,PaymentDate,PaymentMethod) "
        "VALUES (%s,%s,%s,%s,%s)",
        (cid, tid, 0, pdate.strftime('%Y-%m-%d %H:%M:%S'), method)
    )
    invoice_id = cursor.lastrowid

    num_dishes = random.randint(1, 5)
    dish_ids   = random.sample(range(1, 16), num_dishes)
    total      = 0
    for did in dish_ids:
        cursor.execute("SELECT Price FROM MenuItems WHERE DishID=%s", (did,))
        row = cursor.fetchone()
        if row:
            qty        = random.randint(1, 4)
            unit_price = float(row[0])
            total     += qty * unit_price
            cursor.execute(
                "INSERT INTO InvoiceDetails (InvoiceID,DishID,Quantity,UnitPrice) VALUES (%s,%s,%s,%s)",
                (invoice_id, did, qty, unit_price)
            )
    cursor.execute("UPDATE Invoices SET TotalAmount=%s WHERE InvoiceID=%s", (total, invoice_id))

conn.commit()
print("✅ Inserted 300 invoices + details")

cursor.close()
conn.close()
print("\n🎉 Done!")