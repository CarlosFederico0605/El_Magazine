import uuid

from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, abort, make_response)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from models import (obtener_articulo, obtener_encuesta_de_articulo,
                    crear_encuesta, ya_voto, registrar_voto)

encuestas_bp = Blueprint('encuestas', __name__)

class EncuestaForm(FlaskForm):
    pregunta = StringField('Pregunta', validators=[DataRequired()])
    opcion1 = StringField('Opción 1', validators=[DataRequired()])
    opcion2 = StringField('Opción 2', validators=[DataRequired()])
    opcion3 = StringField('Opción 3 (opcional)')
    opcion4 = StringField('Opción 4 (opcional)')
    submit = SubmitField('Crear encuesta')

@encuestas_bp.route('/encuesta/<int:articulo_id>', methods=['GET', 'POST'])
@login_required
def crear(articulo_id):
    art = obtener_articulo(articulo_id)
    if not art:
        abort(404)
    if art['autor_id'] != int(current_user.id) and current_user.rol != 'admin':
        abort(403)
    if obtener_encuesta_de_articulo(articulo_id):
        flash('Este artículo ya tiene una encuesta.', 'warning')
        return redirect(url_for('articulos.ver_articulo', articulo_id=articulo_id))
    form = EncuestaForm()
    if form.validate_on_submit():
        opciones = [form.opcion1.data, form.opcion2.data, form.opcion3.data, form.opcion4.data]
        crear_encuesta(articulo_id, form.pregunta.data, opciones)
        flash('Encuesta creada.', 'success')
        return redirect(url_for('articulos.ver_articulo', articulo_id=articulo_id))
    return render_template('nueva_encuesta.html', form=form, art=art)

@encuestas_bp.route('/votar/<int:encuesta_id>/<int:opcion_id>', methods=['POST'])
def votar(encuesta_id, opcion_id):
    votante = request.cookies.get(f'voto_{encuesta_id}')
    if votante and ya_voto(encuesta_id, votante):
        flash('Ya votaste en esta encuesta.', 'warning')
        return redirect(request.referrer or url_for('articulos.index'))
    if not votante:
        votante = uuid.uuid4().hex
    registrar_voto(encuesta_id, opcion_id, votante)
    resp = make_response(redirect(request.referrer or url_for('articulos.index')))
    resp.set_cookie(f'voto_{encuesta_id}', votante, max_age=60*60*24*365)
    return resp