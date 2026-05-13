from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Table

tables_bp = Blueprint('tables', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_staff'):
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated

@tables_bp.route('/')
@login_required
def index():
    tables = Table.query.order_by(Table.TableNumber).all()
    total      = len(tables)
    available  = sum(1 for t in tables if t.Status == 'available')
    reserved   = sum(1 for t in tables if t.Status == 'reserved')
    return render_template('tables/index.html',
        tables=tables,
        total=total,
        available=available,
        reserved=reserved
    )

@tables_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
def toggle(id):
    table = Table.query.get_or_404(id)
    table.Status = 'reserved' if table.Status == 'available' else 'available'
    db.session.commit()
    flash(f'Table #{table.TableNumber} status updated to {table.Status}.', 'success')
    return redirect(url_for('tables.index'))
@tables_bp.route('/add', methods=['POST'])
@login_required
def add():
    number = request.form.get('number', '').strip()
    if not number:
        flash('Please enter a table number!', 'danger')
        return redirect(url_for('tables.index'))
    existing = Table.query.filter_by(TableNumber=number).first()
    if existing:
        flash(f'Table #{number} already exists!', 'danger')
        return redirect(url_for('tables.index'))
    table = Table(TableNumber=int(number), Status='available')
    db.session.add(table)
    db.session.commit()
    flash(f'Table #{number} added successfully!', 'success')
    return redirect(url_for('tables.index'))