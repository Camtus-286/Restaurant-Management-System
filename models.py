from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'Customers'
    CustomerID   = db.Column(db.Integer, primary_key=True)
    CustomerName = db.Column(db.String(100), nullable=False)
    PhoneNumber  = db.Column(db.String(15), unique=True, nullable=False)
    Address      = db.Column(db.String(255))
    reservations = db.relationship('Reservation', backref='customer', lazy=True)
    invoices     = db.relationship('Invoice',     backref='customer', lazy=True)

class Table(db.Model):
    __tablename__ = 'Tables'
    TableID      = db.Column(db.Integer, primary_key=True)
    TableNumber  = db.Column(db.Integer, unique=True, nullable=False)
    Status       = db.Column(db.Enum('available', 'reserved'), default='available')
    reservations = db.relationship('Reservation', backref='table', lazy=True)
    invoices     = db.relationship('Invoice',     backref='table', lazy=True)

class MenuItem(db.Model):
    __tablename__   = 'MenuItems'
    DishID          = db.Column(db.Integer, primary_key=True)
    DishName        = db.Column(db.String(150), nullable=False)
    Price           = db.Column(db.Numeric(10, 2), nullable=False)
    Category        = db.Column(db.String(50))
    Available       = db.Column(db.Boolean, default=True)
    ImageFilename   = db.Column(db.String(100), default='placeholder.jpg')
    details         = db.relationship('InvoiceDetail', backref='dish', lazy=True)

class Reservation(db.Model):
    __tablename__  = 'Reservations'
    ReservationID  = db.Column(db.Integer, primary_key=True)
    CustomerID     = db.Column(db.Integer, db.ForeignKey('Customers.CustomerID'), nullable=False)
    TableID        = db.Column(db.Integer, db.ForeignKey('Tables.TableID'), nullable=False)
    DateTime       = db.Column(db.DateTime, nullable=False)
    GuestCount     = db.Column(db.Integer, nullable=False)
    # chỉ còn confirmed / cancelled
    Status         = db.Column(db.Enum('confirmed', 'cancelled'), default='confirmed')

class Invoice(db.Model):
    __tablename__  = 'Invoices'
    InvoiceID      = db.Column(db.Integer, primary_key=True)
    CustomerID     = db.Column(db.Integer, db.ForeignKey('Customers.CustomerID'), nullable=False)
    TableID        = db.Column(db.Integer, db.ForeignKey('Tables.TableID'), nullable=False)
    TotalAmount    = db.Column(db.Numeric(10, 2), nullable=False)
    PaymentDate    = db.Column(db.DateTime, server_default=db.func.now())
    PaymentMethod  = db.Column(db.Enum('cash', 'card'), default='cash')
    details        = db.relationship('InvoiceDetail', backref='invoice', lazy=True)
    
class InvoiceDetail(db.Model):
    __tablename__ = 'InvoiceDetails'
    DetailID      = db.Column(db.Integer, primary_key=True)
    InvoiceID     = db.Column(db.Integer, db.ForeignKey('Invoices.InvoiceID'), nullable=False)
    DishID        = db.Column(db.Integer, db.ForeignKey('MenuItems.DishID'), nullable=False)
    Quantity      = db.Column(db.Integer, nullable=False)
    UnitPrice     = db.Column(db.Numeric(10, 2), nullable=False)
   