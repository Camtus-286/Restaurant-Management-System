from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, MenuItem
from sqlalchemy import func
import os
from werkzeug.utils import secure_filename

menu_bp = Blueprint('menu', __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_staff'):
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated

@menu_bp.route('/')
@login_required
def index():
    q        = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    status   = request.args.get('status', '')

    query = MenuItem.query
    if q:
        query = query.filter(MenuItem.DishName.ilike(f'%{q}%'))
    if category:
        query = query.filter_by(Category=category)
    if status == 'available':
        query = query.filter_by(Available=True)
    elif status == 'unavailable':
        query = query.filter_by(Available=False)

    items      = query.order_by(MenuItem.Category, MenuItem.DishName).all()
    categories = [r[0] for r in db.session.query(MenuItem.Category).distinct().all()]
    total      = MenuItem.query.count()
    available  = MenuItem.query.filter_by(Available=True).count()
    avg_price  = db.session.query(func.avg(MenuItem.Price)).scalar() or 0

    return render_template('menu/index.html',
        items=items,
        categories=categories,
        total=total,
        available=available,
        avg_price=avg_price,
        q=q,
        selected_category=category,
        selected_status=status
    )

@menu_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    item = MenuItem.query.get_or_404(id)
    item.DishName  = request.form['name'].strip()
    item.Price     = request.form['price']
    item.Category  = request.form['category'].strip()
    item.Available = request.form.get('available') == 'on'

    file = request.files.get('image')
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'menu')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        item.ImageFilename = filename

    db.session.commit()
    flash('Menu item updated successfully!', 'success')
    return redirect(url_for('menu.index'))
@menu_bp.route('/add', methods=['POST'])
@login_required
def add():
    name     = request.form['name'].strip()
    price    = request.form['price']
    category = request.form['category'].strip()

    item = MenuItem(
        DishName  = name,
        Price     = price,
        Category  = category,
        Available = True
    )
    db.session.add(item)
    db.session.flush()

    file = request.files.get('image')
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'menu')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        item.ImageFilename = filename

    db.session.commit()
    flash('Dish added successfully!', 'success')
    return redirect(url_for('menu.index'))