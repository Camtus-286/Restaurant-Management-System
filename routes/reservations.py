from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Reservation, Customer, Table
from datetime import datetime

reservations_bp = Blueprint('reservations', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_staff'):
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated

@reservations_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '')
    q      = request.args.get('q', '').strip()

    query = Reservation.query.join(Customer)
    if status in ('confirmed', 'cancelled'):
        query = query.filter(Reservation.Status == status)
    if q:
        query = query.filter(Customer.CustomerName.ilike(f'%{q}%'))

    reservations     = query.order_by(Reservation.DateTime.desc()).all()
    customers        = Customer.query.order_by(Customer.CustomerName).all()
    available_tables = Table.query.filter_by(Status='available')\
                           .order_by(Table.TableNumber).all()
    confirmed_count  = Reservation.query.filter_by(Status='confirmed').count()
    cancelled_count  = Reservation.query.filter_by(Status='cancelled').count()

    return render_template('reservations/index.html',
        reservations=reservations,
        customers=customers,
        available_tables=available_tables,
        confirmed_count=confirmed_count,
        cancelled_count=cancelled_count,
        selected_status=status,
        q=q
    )

@reservations_bp.route('/add', methods=['POST'])
@login_required
def add():
    table = Table.query.get(request.form['table_id'])
    if not table or table.Status == 'reserved':
        flash('This table is not available!', 'danger')
        return redirect(url_for('reservations.index'))

    reservation = Reservation(
        CustomerID = request.form['customer_id'],
        TableID    = request.form['table_id'],
        DateTime   = datetime.strptime(request.form['datetime'], '%Y-%m-%dT%H:%M'),
        GuestCount = int(request.form['guest_count']),
        Status     = 'confirmed'
    )
    table.Status = 'reserved'
    db.session.add(reservation)
    db.session.commit()
    flash('Reservation confirmed!', 'success')
    return redirect(url_for('reservations.index'))

@reservations_bp.route('/cancel/<int:id>', methods=['POST'])
@login_required
def cancel(id):
    reservation = Reservation.query.get_or_404(id)
    if reservation.Status == 'cancelled':
        flash('Reservation is already cancelled.', 'warning')
        return redirect(url_for('reservations.index'))
    reservation.Status = 'cancelled'
    table = Table.query.get(reservation.TableID)
    if table:
        table.Status = 'available'
    db.session.commit()
    flash('Reservation cancelled.', 'warning')
    return redirect(url_for('reservations.index'))