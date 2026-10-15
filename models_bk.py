from database import get_db
from werkzeug.security import generate_password_hash

# ---------- Usuarios ----------
def obtener_usuario_por_username(username):
    conn = get_db()
    row = conn.execute("SELECT * FROM usuarios WHERE username=?", (username,)).fetchone()
    conn.close()
    return row

def obtener_usuario_por_id(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM usuarios WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return row

def listar_usuarios():
    conn = get_db()
    rows = conn.execute("SELECT * FROM usuarios ORDER BY id").fetchall()
    conn.close()
    return rows

def crear_usuario(username, password, rol='escritor'):
    conn = get_db()
    try:
        conn.execute("INSERT INTO usuarios (username, password, rol, activo) VALUES (?,?,?,1)",
                     (username, generate_password_hash(password), rol))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def toggle_usuario(user_id):
    conn = get_db()
    u = conn.execute("SELECT * FROM usuarios WHERE id=?", (user_id,)).fetchone()
    if u and u['rol'] != 'admin':
        conn.execute("UPDATE usuarios SET activo=? WHERE id=?",
                     (0 if u['activo'] else 1, user_id))
        conn.commit()
    conn.close()

# ---------- Artículos ----------
def listar_articulos_publicados():
    conn = get_db()
    rows = conn.execute('''SELECT a.*, u.username AS autor FROM articulos a
                           JOIN usuarios u ON u.id = a.autor_id
                           WHERE a.estado='publicado'
                           ORDER BY a.fecha DESC''').fetchall()
    conn.close()
    return rows

def listar_articulos_de_usuario(user_id):
    conn = get_db()
    rows = conn.execute('''SELECT a.*, u.username AS autor FROM articulos a
                           JOIN usuarios u ON u.id = a.autor_id
                           WHERE a.autor_id=? ORDER BY a.fecha DESC''', (user_id,)).fetchall()
    conn.close()
    return rows

def listar_todos_articulos():
    conn = get_db()
    rows = conn.execute('''SELECT a.*, u.username AS autor FROM articulos a
                           JOIN usuarios u ON u.id = a.autor_id
                           ORDER BY a.fecha DESC''').fetchall()
    conn.close()
    return rows

def obtener_articulo(articulo_id):
    conn = get_db()
    row = conn.execute('''SELECT a.*, u.username AS autor FROM articulos a
                          JOIN usuarios u ON u.id = a.autor_id
                          WHERE a.id=?''', (articulo_id,)).fetchone()
    conn.close()
    return row

def crear_articulo(titulo, contenido, autor_id, imagen, fecha):
    conn = get_db()
    conn.execute('''INSERT INTO articulos (titulo, contenido, autor_id, imagen, estado, fecha)
                    VALUES (?,?,?,?,?,?)''',
                 (titulo, contenido, autor_id, imagen, 'pendiente', fecha))
    conn.commit()
    conn.close()

def actualizar_articulo(articulo_id, titulo, contenido, imagen=None):
    conn = get_db()
    if imagen:
        conn.execute('''UPDATE articulos SET titulo=?, contenido=?, imagen=?, estado='pendiente'
                        WHERE id=?''', (titulo, contenido, imagen, articulo_id))
    else:
        conn.execute('''UPDATE articulos SET titulo=?, contenido=?, estado='pendiente'
                        WHERE id=?''', (titulo, contenido, articulo_id))
    conn.commit()
    conn.close()

def cambiar_estado_articulo(articulo_id, estado):
    conn = get_db()
    conn.execute("UPDATE articulos SET estado=? WHERE id=?", (estado, articulo_id))
    conn.commit()
    conn.close()

def publicar_articulo(articulo_id, qr):
    conn = get_db()
    conn.execute("UPDATE articulos SET estado='publicado', qr=? WHERE id=?", (qr, articulo_id))
    conn.commit()
    conn.close()

def incrementar_vistas(articulo_id):
    conn = get_db()
    conn.execute("UPDATE articulos SET vistas = vistas + 1 WHERE id=?", (articulo_id,))
    conn.commit()
    conn.close()

# ---------- Encuestas ----------
def obtener_encuesta_de_articulo(articulo_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM encuestas WHERE articulo_id=?", (articulo_id,)).fetchone()
    conn.close()
    return row

def listar_opciones(encuesta_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM opciones WHERE encuesta_id=?", (encuesta_id,)).fetchall()
    conn.close()
    return rows

def crear_encuesta(articulo_id, pregunta, opciones):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO encuestas (articulo_id, pregunta) VALUES (?,?)",
                (articulo_id, pregunta))
    enc_id = cur.lastrowid
    for op in opciones:
        if op and op.strip():
            cur.execute("INSERT INTO opciones (encuesta_id, texto) VALUES (?,?)",
                        (enc_id, op.strip()))
    conn.commit()
    conn.close()

def ya_voto(encuesta_id, votante):
    conn = get_db()
    row = conn.execute("SELECT 1 FROM votos WHERE encuesta_id=? AND votante=?",
                       (encuesta_id, votante)).fetchone()
    conn.close()
    return bool(row)

def registrar_voto(encuesta_id, opcion_id, votante):
    conn = get_db()
    conn.execute("INSERT INTO votos (encuesta_id, opcion_id, votante) VALUES (?,?,?)",
                 (encuesta_id, opcion_id, votante))
    conn.execute("UPDATE opciones SET votos = votos + 1 WHERE id=?", (opcion_id,))
    conn.commit()
    conn.close()