import os

from flask import Flask
from flask_login import LoginManager
from models import obtener_fondo
from database import init_db, get_db
from auth import auth_bp, Usuario
from articulos import articulos_bp
from encuestas import encuestas_bp
from admin import admin_bp
from config import SECRET_KEY, MAX_CONTENT_LENGTH, UPLOAD_FOLDER, QR_FOLDER, FONDO_FOLDER

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(FONDO_FOLDER, exist_ok=True)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM usuarios WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return Usuario(row) if row else None

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(articulos_bp)
app.register_blueprint(encuestas_bp)
app.register_blueprint(admin_bp)

init_db()

if __name__ == '__main__':
    app.run(debug=False)
    
@app.context_processor
def inyectar_fondo():
    return dict(fondo_global=obtener_fondo())    