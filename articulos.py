from datetime import datetime

from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, abort, make_response)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from models import (listar_articulos_publicados, listar_articulos_de_usuario,
                    obtener_articulo, crear_articulo, actualizar_articulo,
                    cambiar_estado_articulo, incrementar_vistas,
                    obtener_encuesta_de_articulo, listar_opciones, ya_voto,
                    obtener_destacado, listar_mas_leidos, listar_autores_publicados,
                    obtener_fondo)
                    
from models import obtener_fondo
from utils import guardar_imagen

articulos_bp = Blueprint('articulos', __name__)

class ArticuloForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    contenido = TextAreaField('Contenido', validators=[DataRequired()])
    submit = SubmitField('Guardar')

@articulos_bp.route('/')
def index():
    busqueda = request.args.get('q', '').strip() or None
    autor = request.args.get('autor', '').strip() or None

    destacado = obtener_destacado() if not busqueda and not autor else None
    mas_leido = listar_mas_leidos(1)
    recientes = listar_articulos_publicados()
    autores = listar_autores_publicados()
    articulos = listar_articulos_publicados(busqueda=busqueda, autor=autor)
    fondo = obtener_fondo()

    return render_template('index.html',
                           articulos=articulos,
                           destacado=destacado,
                           mas_leido=mas_leido[0] if mas_leido else None,
                           recientes=recientes,
                           autores=autores,
                           fondo=fondo,
                           busqueda=busqueda or '',
                           autor_actual=autor or '')
                           
@articulos_bp.route('/articulo/<int:articulo_id>')
def ver_articulo(articulo_id):
    art = obtener_articulo(articulo_id)
    if not art:
        abort(404)
    if art['estado'] != 'publicado':
        if not current_user.is_authenticated:
            abort(404)
        if current_user.rol != 'admin' and str(art['autor_id']) != current_user.id:
            abort(403)
    if art['estado'] == 'publicado':
        incrementar_vistas(articulo_id)

    encuesta = obtener_encuesta_de_articulo(articulo_id)
    opciones = []
    voto_existente = False
    if encuesta:
        opciones = listar_opciones(encuesta['id'])
        votante = request.cookies.get(f'voto_{encuesta["id"]}')
        if votante:
            voto_existente = ya_voto(encuesta['id'], votante)
    return render_template('articulo.html', art=art, encuesta=encuesta,
                           opciones=opciones, ya_voto=voto_existente)

@articulos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_articulo():
    form = ArticuloForm()
    if form.validate_on_submit():
        imagen = guardar_imagen(request.files.get('imagen'))
        crear_articulo(form.titulo.data, form.contenido.data, current_user.id,
                       imagen, datetime.now().strftime('%Y-%m-%d %H:%M'))
        flash('Artículo creado. Esperando aprobación del administrador.', 'success')
        return redirect(url_for('articulos.mis_articulos'))
    return render_template('nuevo_articulo.html', form=form)

@articulos_bp.route('/mis-articulos')
@login_required
def mis_articulos():
    arts = listar_articulos_de_usuario(current_user.id)
    return render_template('mis_articulos.html', articulos=arts)

@articulos_bp.route('/editar/<int:articulo_id>', methods=['GET', 'POST'])
@login_required
def editar_articulo(articulo_id):
    art = obtener_articulo(articulo_id)
    if not art:
        abort(404)
    if art['autor_id'] != int(current_user.id) and current_user.rol != 'admin':
        abort(403)
    if art['estado'] == 'publicado':
        flash('Un artículo publicado no se puede editar.', 'warning')
        return redirect(url_for('articulos.mis_articulos'))
    form = ArticuloForm(data={'titulo': art['titulo'], 'contenido': art['contenido']})
    if form.validate_on_submit():
        nueva = guardar_imagen(request.files.get('imagen'))
        actualizar_articulo(articulo_id, form.titulo.data, form.contenido.data, nueva)
        flash('Artículo actualizado y enviado a revisión.', 'success')
        return redirect(url_for('articulos.mis_articulos'))
    return render_template('nuevo_articulo.html', form=form, editar=True)

@articulos_bp.route('/retirar/<int:articulo_id>', methods=['POST'])
@login_required
def retirar_articulo(articulo_id):
    art = obtener_articulo(articulo_id)
    if not art:
        abort(404)
    if art['autor_id'] != int(current_user.id) and current_user.rol != 'admin':
        abort(403)
    cambiar_estado_articulo(articulo_id, 'retirado')
    flash('Artículo retirado.', 'info')
    return redirect(request.referrer or url_for('articulos.index'))