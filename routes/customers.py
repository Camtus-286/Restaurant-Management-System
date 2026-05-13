from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Customer, Invoice, Reservation
from sqlalchemy import func

customers_bp = Blueprint('customers', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_staff'):
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated

@customers_bp.route('/')
@login_required
def index():
    q = request.args.get('q', '').strip()
    if q:
        customers = Customer.query.filter(
            db.or_(
                Customer.CustomerName.ilike(f'%{q}%'),
                Customer.PhoneNumber.ilike(f'%{q}%')
            )
        ).order_by(Customer.CustomerID.desc()).all()
    else:
        customers = Customer.query.order_by(Customer.CustomerID.desc()).all()
    return render_template('customers/index.html', customers=customers, q=q)

@customers_bp.route('/view/<int:id>')
@login_required
def view(id):
    customer = Customer.query.get_or_404(id)
    invoices = Invoice.query.filter_by(CustomerID=id)\
        .order_by(Invoice.PaymentDate.desc()).limit(10).all()
    reservations = Reservation.query.filter_by(CustomerID=id)\
        .order_by(Reservation.DateTime.desc()).limit(10).all()
    total_spent = db.session.query(
        func.coalesce(func.sum(Invoice.TotalAmount), 0)
    ).filter_by(CustomerID=id).scalar() or 0
    return render_template('customers/view.html',
        customer=customer,
        invoices=invoices,
        reservations=reservations,
        total_spent=total_spent
    )

@customers_bp.route('/add', methods=['POST'])
@login_required
def add():
    existing = Customer.query.filter_by(PhoneNumber=request.form['phone']).first()
    if existing:
        flash('Phone number already exists!', 'danger')
        return redirect(url_for('customers.index'))
    customer = Customer(
        CustomerName = request.form['name'].strip(),
        PhoneNumber  = request.form['phone'].strip(),
        Address      = request.form.get('address', '').strip()
    )
    db.session.add(customer)
    db.session.commit()
    flash('Customer added successfully!', 'success')
    return redirect(url_for('customers.index'))

@customers_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    customer = Customer.query.get_or_404(id)
    existing = Customer.query.filter(
        Customer.PhoneNumber == request.form['phone'],
        Customer.CustomerID != id
    ).first()
    if existing:
        flash('Phone number already used by another customer!', 'danger')
        return redirect(url_for('customers.index'))
    customer.CustomerName = request.form['name'].strip()
    customer.PhoneNumber  = request.form['phone'].strip()
    customer.Address      = request.form.get('address', '').strip()
    db.session.commit()
    flash('Customer updated successfully!', 'success')
    return redirect(url_for('customers.index'))

@customers_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted!', 'warning')
    return redirect(url_for('customers.index'))