import os
import uuid
from functools import wraps

import qrcode
from flask import abort, url_for
from flask_login import current_user

from config import UPLOAD_FOLDER, QR_FOLDER, ALLOWED_EXT
from config import FONDO_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def guardar_imagen(file):
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    nombre = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(UPLOAD_FOLDER, nombre))
    return nombre

def generar_qr(articulo_id):
    url = url_for('articulos.ver_articulo', articulo_id=articulo_id, _external=True)
    img = qrcode.make(url)
    nombre = f"qr_{articulo_id}.png"
    img.save(os.path.join(QR_FOLDER, nombre))
    return nombre

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return wrapper

def guardar_imagen_fondo(file):
    """Guarda la imagen de fondo y borra la anterior si existía."""
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None
    # Borra la imagen anterior de la carpeta
    if os.path.isdir(FONDO_FOLDER):
        for f in os.listdir(FONDO_FOLDER):
            try:
                os.remove(os.path.join(FONDO_FOLDER, f))
            except Exception:
                pass
    ext = file.filename.rsplit('.', 1)[1].lower()
    nombre = f"fondo.{ext}"
    file.save(os.path.join(FONDO_FOLDER, nombre))
    return nombre