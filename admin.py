from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from models import (listar_usuarios, crear_usuario, toggle_usuario,
                    listar_todos_articulos, publicar_articulo,
                    cambiar_estado_articulo, guardar_fondo, obtener_fondo)
from utils import admin_required, generar_qr, guardar_imagen_fondo

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

class UsuarioForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Crear usuario')

@admin_bp.route('/usuarios', methods=['GET', 'POST'])
@login_required
@admin_required
def usuarios():
    form = UsuarioForm()
    if form.validate_on_submit():
        if crear_usuario(form.username.data, form.password.data):
            flash('Usuario creado.', 'success')
        else:
            flash('Ese usuario ya existe.', 'danger')
    return render_template('admin_usuarios.html', form=form, usuarios=listar_usuarios())

@admin_bp.route('/usuario/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle(user_id):
    toggle_usuario(user_id)
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/articulos')
@login_required
@admin_required
def articulos():
    return render_template('admin_articulos.html', articulos=listar_todos_articulos())

@admin_bp.route('/publicar/<int:articulo_id>', methods=['POST'])
@login_required
@admin_required
def publicar(articulo_id):
    qr = generar_qr(articulo_id)
    publicar_articulo(articulo_id, qr)
    flash('Artículo publicado y QR generado.', 'success')
    return redirect(url_for('admin.articulos'))

@admin_bp.route('/rechazar/<int:articulo_id>', methods=['POST'])
@login_required
@admin_required
def rechazar(articulo_id):
    cambiar_estado_articulo(articulo_id, 'rechazado')
    flash('Artículo rechazado.', 'info')
    return redirect(url_for('admin.articulos'))

@admin_bp.route('/fondo', methods=['GET', 'POST'])
@login_required
@admin_required
def fondo():
    if request.method == 'POST':
        archivo = request.files.get('imagen')
        nombre = guardar_imagen_fondo(archivo)
        if nombre:
            guardar_fondo(nombre)
            flash('Fondo actualizado.', 'success')
        else:
            flash('Archivo no válido. Usa JPG, PNG, GIF o WEBP.', 'danger')
        return redirect(url_for('admin.fondo'))
    return render_template('admin_fondo.html', fondo=obtener_fondo())