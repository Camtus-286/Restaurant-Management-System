from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, Customer, Table, Reservation, Invoice, InvoiceDetail, MenuItem
from config import Config
from datetime import datetime, date, timedelta
from sqlalchemy import func

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

STAFF_USERNAME = 'admin'
STAFF_PASSWORD = 'Staff@1234'

# ── Blueprints ────────────────────────────────────────────
from routes.customers    import customers_bp
from routes.tables       import tables_bp
from routes.menu         import menu_bp
from routes.reservations import reservations_bp
from routes.invoices     import invoices_bp
from routes.reports      import reports_bp

app.register_blueprint(customers_bp,    url_prefix='/customers')
app.register_blueprint(tables_bp,       url_prefix='/tables')
app.register_blueprint(menu_bp,         url_prefix='/menu')
app.register_blueprint(reservations_bp, url_prefix='/reservations')
app.register_blueprint(invoices_bp,     url_prefix='/invoices')
app.register_blueprint(reports_bp,      url_prefix='/reports')

# ── Auth helper ───────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_staff'):
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated

# ── Routes ────────────────────────────────────────────────
@app.route('/')
def home():
    if session.get('is_staff'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('staff_login'))

@app.route('/login', methods=['GET', 'POST'])
def staff_login():
    error = None
    if session.get('is_staff'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == STAFF_USERNAME and password == STAFF_PASSWORD:
            session['is_staff'] = True
            return redirect(url_for('dashboard'))
        error = 'Incorrect username or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('staff_login'))

# ── Customer Search API (autocomplete) ────────────────────
@app.route('/customers/search')
@login_required
def customer_search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    results = Customer.query.filter(
        db.or_(
            Customer.CustomerName.ilike(f'%{q}%'),
            Customer.PhoneNumber.ilike(f'%{q}%')
        )
    ).limit(8).all()
    return jsonify([{
        'id':      c.CustomerID,
        'name':    c.CustomerName,
        'phone':   c.PhoneNumber,
        'address': c.Address or ''
    } for c in results])
@app.route('/tables/available')
@login_required
def tables_available():
    dt_str = request.args.get('datetime', '')
    if not dt_str:
        tables = Table.query.filter_by(Status='available').order_by(Table.TableNumber).all()
        return jsonify([{'id': t.TableID, 'number': t.TableNumber} for t in tables])
    
    try:
        dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M')
    except:
        return jsonify([])

    # Tìm bàn không có reservation confirmed trong vòng ±2h
    from sqlalchemy import and_, or_, not_, exists
    busy_tables = db.session.query(Reservation.TableID).filter(
        Reservation.Status == 'confirmed',
        Reservation.DateTime.between(
            dt - timedelta(hours=2),
            dt + timedelta(hours=2)
        )
    ).subquery()

    free_tables = Table.query.filter(
        Table.Status == 'available',
        ~Table.TableID.in_(busy_tables)
    ).order_by(Table.TableNumber).all()

    return jsonify([{'id': t.TableID, 'number': t.TableNumber} for t in free_tables])
# ── Dashboard ─────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()

    total_customers    = Customer.query.count()
    available_tables   = Table.query.filter_by(Status='available').count()
    today_reservations = Reservation.query.filter(
        func.date(Reservation.DateTime) == today,
        Reservation.Status == 'confirmed'
    ).count()
    today_revenue = db.session.query(
        func.coalesce(func.sum(Invoice.TotalAmount), 0)
    ).filter(func.date(Invoice.PaymentDate) == today).scalar() or 0

    recent_reservations = (
        Reservation.query
        .filter(func.date(Reservation.DateTime) == today)
        .order_by(Reservation.DateTime.asc())
        .limit(8).all()
    )

    top_dishes = (
        db.session.query(
            MenuItem.DishName,
            func.sum(InvoiceDetail.Quantity).label('total_sold'),
            func.sum(InvoiceDetail.Quantity * InvoiceDetail.UnitPrice).label('revenue')
        )
        .join(InvoiceDetail, MenuItem.DishID == InvoiceDetail.DishID)
        .group_by(MenuItem.DishID, MenuItem.DishName)
        .order_by(func.sum(InvoiceDetail.Quantity).desc())
        .limit(5).all()
    )

    chart_labels, chart_data = [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        rev = db.session.query(
            func.coalesce(func.sum(Invoice.TotalAmount), 0)
        ).filter(func.date(Invoice.PaymentDate) == day).scalar() or 0
        chart_labels.append(day.strftime('%d/%m'))
        chart_data.append(float(rev))

    return render_template('dashboard.html',
        total_customers=total_customers,
        available_tables=available_tables,
        today_reservations=today_reservations,
        today_revenue=today_revenue,
        recent_reservations=recent_reservations,
        top_dishes=top_dishes,
        chart_labels=chart_labels,
        chart_data=chart_data,
        now=datetime.now()
    )

if __name__ == '__main__':
    app.run(debug=True)