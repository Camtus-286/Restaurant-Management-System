from flask import Blueprint, render_template, request, session, redirect, url_for
from models import db, Invoice, InvoiceDetail, MenuItem, Reservation
from sqlalchemy import func
from datetime import date, timedelta

reports_bp = Blueprint('reports', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_staff'):
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated

@reports_bp.route('/')
@login_required
def index():
    days      = int(request.args.get('days', 30))
    today     = date.today()
    start     = today - timedelta(days=days - 1)

    # ── Summary ────────────────────────────────────────────
    total_revenue = db.session.query(
        func.coalesce(func.sum(Invoice.TotalAmount), 0)
    ).filter(func.date(Invoice.PaymentDate) >= start).scalar() or 0

    total_invoices = Invoice.query.filter(
        func.date(Invoice.PaymentDate) >= start
    ).count()

    avg_invoice = float(total_revenue) / total_invoices if total_invoices else 0

    # ── Revenue chart (daily) ──────────────────────────────
    chart_labels, chart_data = [], []
    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)
        rev = db.session.query(
            func.coalesce(func.sum(Invoice.TotalAmount), 0)
        ).filter(func.date(Invoice.PaymentDate) == day).scalar() or 0
        chart_labels.append(day.strftime('%d/%m'))
        chart_data.append(float(rev))

    # ── Payment method breakdown ───────────────────────────
    cash_total = db.session.query(
        func.coalesce(func.sum(Invoice.TotalAmount), 0)
    ).filter(Invoice.PaymentMethod == 'cash',
             func.date(Invoice.PaymentDate) >= start).scalar() or 0

    card_total = db.session.query(
        func.coalesce(func.sum(Invoice.TotalAmount), 0)
    ).filter(Invoice.PaymentMethod == 'card',
             func.date(Invoice.PaymentDate) >= start).scalar() or 0

    # ── Top dishes ─────────────────────────────────────────
    top_dishes = (
        db.session.query(
            MenuItem.DishName,
            MenuItem.Category,
            func.sum(InvoiceDetail.Quantity).label('total_sold'),
            func.sum(InvoiceDetail.Quantity * InvoiceDetail.UnitPrice).label('revenue')
        )
        .join(InvoiceDetail, MenuItem.DishID == InvoiceDetail.DishID)
        .join(Invoice, InvoiceDetail.InvoiceID == Invoice.InvoiceID)
        .filter(func.date(Invoice.PaymentDate) >= start)
        .group_by(MenuItem.DishID, MenuItem.DishName, MenuItem.Category)
        .order_by(func.sum(InvoiceDetail.Quantity * InvoiceDetail.UnitPrice).desc())
        .limit(10).all()
    )

    # ── Reservation status breakdown ───────────────────────
    confirmed_count = Reservation.query.filter_by(Status='confirmed').count()
    cancelled_count = Reservation.query.filter_by(Status='cancelled').count()

    return render_template('reports/index.html',
        days=days,
        total_revenue=total_revenue,
        total_invoices=total_invoices,
        avg_invoice=avg_invoice,
        chart_labels=chart_labels,
        chart_data=chart_data,
        cash_total=cash_total,
        card_total=card_total,
        top_dishes=top_dishes,
        confirmed_count=confirmed_count,
        cancelled_count=cancelled_count,
    )