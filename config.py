import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'datos.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
QR_FOLDER = os.path.join(BASE_DIR, 'static', 'qr')
FONDO_FOLDER = os.path.join(BASE_DIR, 'static', 'fondo')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
SECRET_KEY = 'c46e1d54a4b7fc84e0c3c48a6ecd82708ab406fa02f1cec4bab50d22cec26db6'
MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB