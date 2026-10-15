
from flask_login import login_user, logout_user, login_required, UserMixin
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash

from models import obtener_usuario_por_username

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class Usuario(UserMixin):
    def __init__(self, row):
        self.id = str(row['id'])
        self.username = row['username']
        self.rol = row['rol']
        self.activo = row['activo']

    @property
    def is_active(self):
        return bool(self.activo)

    def get_id(self):
        return self.id

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        row = obtener_usuario_por_username(form.username.data)
        if row and row['activo'] and check_password_hash(row['password'], form.password.data):
            login_user(Usuario(row))
            return redirect(url_for('articulos.index'))
        flash('Usuario o contraseña incorrectos, o cuenta desactivada.', 'danger')
        flash('Usuario o contraseña incorrectos, o cuenta desactivada.', 'danger')      
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))