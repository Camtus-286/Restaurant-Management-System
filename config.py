from sqlalchemy.engine import URL

connection_url = URL.create(
    drivername='mysql+pymysql',
    username='root',
    password='Leecamtus@123',
    host='localhost',
    database='restaurant_db'
)

class Config:
    SQLALCHEMY_DATABASE_URI = connection_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'restaurant-secret-key-2024'