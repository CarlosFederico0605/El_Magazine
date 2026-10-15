import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'datos.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
QR_FOLDER = os.path.join(BASE_DIR, 'static', 'qr')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
SECRET_KEY = 'cambia-esta-clave-por-algo-secreto'
MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB