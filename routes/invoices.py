from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Invoice, InvoiceDetail, Customer, Table, MenuItem
from sqlalchemy import func
from datetime import datetime

invoices_bp = Blueprint('invoices', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_staff'):
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated

@invoices_bp.route('/')
@login_required
def index():
    q         = request.args.get('q', '').strip()
    method    = request.args.get('method', '')
    date_from = request.args.get('date_from', '')
    date_to   = request.args.get('date_to', '')

    query = Invoice.query.join(Customer)
    if q:
        query = query.filter(
            db.or_(
                Customer.CustomerName.ilike(f'%{q}%'),
                Customer.PhoneNumber.ilike(f'%{q}%')
            )
        )
    if method in ('cash', 'card'):
        query = query.filter(Invoice.PaymentMethod == method)
    if date_from:
        query = query.filter(Invoice.PaymentDate >= date_from)
    if date_to:
        query = query.filter(Invoice.PaymentDate <= date_to + ' 23:59:59')

    invoices       = query.order_by(Invoice.PaymentDate.desc()).all()
    total_revenue  = db.session.query(func.coalesce(func.sum(Invoice.TotalAmount), 0)).scalar() or 0
    total_invoices = Invoice.query.count()
    cash_total     = db.session.query(func.coalesce(func.sum(Invoice.TotalAmount), 0))\
                        .filter_by(PaymentMethod='cash').scalar() or 0
    card_total     = db.session.query(func.coalesce(func.sum(Invoice.TotalAmount), 0))\
                        .filter_by(PaymentMethod='card').scalar() or 0
    customers  = Customer.query.order_by(Customer.CustomerName).all()
    tables     = Table.query.order_by(Table.TableNumber).all()
    menu_items = MenuItem.query.filter_by(Available=True).order_by(MenuItem.Category, MenuItem.DishName).all()

    return render_template('invoices/index.html',
        invoices=invoices,
        total_revenue=total_revenue,
        total_invoices=total_invoices,
        cash_total=cash_total,
        card_total=card_total,
        customers=customers,
        tables=tables,
        menu_items=menu_items,
        q=q,
        selected_method=method,
        date_from=date_from,
        date_to=date_to
    )

@invoices_bp.route('/view/<int:id>')
@login_required
def view(id):
    invoice = Invoice.query.get_or_404(id)
    details = InvoiceDetail.query.filter_by(InvoiceID=id).all()
    return render_template('invoices/view.html', invoice=invoice, details=details)

@invoices_bp.route('/add', methods=['POST'])
@login_required
def add():
    dish_ids   = request.form.getlist('dish_id[]')
    quantities = request.form.getlist('quantity[]')

    if not dish_ids:
        flash('Please add at least one dish!', 'danger')
        return redirect(url_for('invoices.index'))

    invoice = Invoice(
        CustomerID    = request.form['customer_id'],
        TableID       = request.form['table_id'],
        TotalAmount   = 0,
        PaymentMethod = request.form.get('payment_method', 'cash'),
        PaymentDate   = datetime.now()
    )
    db.session.add(invoice)
    db.session.flush()

    total = 0
    for dish_id, qty in zip(dish_ids, quantities):
        dish = MenuItem.query.get(dish_id)
        if dish and int(qty) > 0:
            qty_int  = int(qty)
            subtotal = float(dish.Price) * qty_int
            total   += subtotal
            db.session.add(InvoiceDetail(
                InvoiceID = invoice.InvoiceID,
                DishID    = dish_id,
                Quantity  = qty_int,
                UnitPrice = dish.Price
            ))

    invoice.TotalAmount = total

    # Auto-release table
    table = Table.query.get(int(request.form['table_id']))
    if table:
        table.Status = 'available'

    db.session.commit()
    flash('Invoice created successfully!', 'success')
    return redirect(url_for('invoices.index'))