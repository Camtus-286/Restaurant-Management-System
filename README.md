# Restaurant Management System

> Project 05 – End Term Project | DATCOM Lab | National Economics University

A web-based restaurant management system built with **Flask** and **MySQL**, designed to streamline daily restaurant operations including customer management, table reservations, menu management, invoicing, and revenue reporting.

---

## Author

| Field | Info |
|-------|------|
| Student | Le Cam Tu |
| Student ID | 11245945 |
| Class | DSEB 66B |
| GitHub | [@Camtus-286](https://github.com/Camtus-286) |

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.12 | Programming language |
| Flask 3.1.3 | Web framework |
| Flask-SQLAlchemy | ORM for database operations |
| MySQL | Database management system |
| PyMySQL | MySQL driver |
| Jinja2 | HTML templating |
| Chart.js | Revenue charts |

---

## Project Structure

```
Restaurant-Management-System/
├── app.py                  # Main Flask application
├── config.py               # Database configuration
├── models.py               # SQLAlchemy models
├── generate_data.py        # Sample data generation script
├── requirements.txt        # Python dependencies
├── routes/
│   ├── customers.py        # Customer CRUD + detail view
│   ├── tables.py           # Table management
│   ├── menu.py             # Menu + image upload
│   ├── reservations.py     # Reservation booking + cancel
│   ├── invoices.py         # Invoice creation + filtering
│   └── reports.py          # Revenue analytics
├── templates/
│   ├── base.html           # Base layout (Borcelle theme)
│   ├── login.html          # Staff login page
│   ├── dashboard.html      # Main dashboard
│   ├── customers/
│   ├── tables/
│   ├── menu/
│   ├── reservations/
│   ├── invoices/
│   └── reports/
└── static/
    ├── css/
    └── images/menu/        # Dish photographs
```

---

## Database Schema

**6 Tables:**
- `Customers` — customer identity and contact details
- `Tables` — restaurant tables with available/reserved status
- `MenuItems` — dishes with categories, prices, and images
- `Reservations` — table bookings with date/time and guest count
- `Invoices` — billing records per dining session
- `InvoiceDetails` — line items linking invoices to dishes

**Advanced Database Objects:**
- 7 Indexes — optimized queries on phone, name, date, customer
- 3 Views — `v_daily_bookings`, `v_table_availability`, `v_top_selling_dishes`
- 2 Stored Procedures — `sp_confirm_reservation`, `sp_generate_invoice`
- 1 User Defined Function — `fn_calculate_discount`
- 2 Triggers — `trg_reserve_table`, `trg_release_table_on_cancel`

---

## Features

-  **Authentication** — session-based staff login
-  **Dashboard** — real-time stats, today's reservations, top dishes, 7-day revenue chart
-  **Customer Management** — add, edit, search, view invoice & reservation history
-  **Table Management** — 20 tables, toggle available/reserved, add new tables
-  **Menu Management** — 15 dishes, 5 categories, image upload, filter by category/status
-  **Reservations** — create, cancel, auto table status update
-  **Invoices** — create with dish selection, filter by method/date, auto table release
-  **Reports** — revenue charts, top 10 dishes, reservation breakdown (7/30/90 days)
-  **Smart Search** — autocomplete customer search in reservation and invoice forms
-  **Smart Table Availability** — shows only tables free within ±2 hours of selected time
-  **Advanced Filtering** — filter reservations by date, sort by last added or date
-  **Customer Autocomplete** — smart search suggests existing customers while typing in reservation and invoice forms
-  **Smart Table Availability** — automatically filters available tables based on selected date/time (±2 hour conflict check)
-  **Advanced Reservation Filter** — filter by date, sort by last added or date ascending/descending
-  **Auto-create Customer** — new customers are automatically added to the system when booking a reservation
---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Camtus-286/Restaurant-Management-System.git
cd Restaurant-Management-System
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup MySQL database
- Open MySQL Workbench
- Run `restaurant_db_complete.sql` to create all tables, indexes, views, procedures, and triggers

### 4. Configure database connection
Edit `config.py` with your MySQL credentials:
```python
connection_url = URL.create(
    drivername='mysql+pymysql',
    username='root',
    password='your_password',
    host='localhost',
    database='restaurant_db'
)
```

### 5. Generate sample data
```bash
python3 generate_data.py
```

### 6. Run the application
```bash
python3 app.py
```

Visit `http://127.0.0.1:5000` and login with:
- **Username:** `admin`
- **Password:** `Staff@1234`

---

## Sample Data

| Table | Rows | Description |
|-------|------|-------------|
| Customers | 100 | English names, Vietnamese phone numbers |
| Tables | 20 | Table numbers 1-20 |
| MenuItems | 15 | Italian/Western dishes, 5 categories |
| Reservations | 100 | Last 60 days to next 30 days |
| Invoices | 300 | Last 30 days, cash/card payment |
| InvoiceDetails | ~900 | 1-5 dishes per invoice |

---

## License

This project is for academic purposes only — DATCOM Lab, NEU College of Technology.
