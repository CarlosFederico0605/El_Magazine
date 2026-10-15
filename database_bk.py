import sqlite3
from werkzeug.security import generate_password_hash
from config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL DEFAULT 'escritor',
        activo INTEGER NOT NULL DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS articulos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        contenido TEXT NOT NULL,
        autor_id INTEGER NOT NULL,
        imagen TEXT,
        estado TEXT NOT NULL DEFAULT 'pendiente',
        vistas INTEGER NOT NULL DEFAULT 0,
        qr TEXT,
        fecha TEXT NOT NULL,
        FOREIGN KEY (autor_id) REFERENCES usuarios(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS encuestas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        articulo_id INTEGER UNIQUE NOT NULL,
        pregunta TEXT NOT NULL,
        FOREIGN KEY (articulo_id) REFERENCES articulos(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS opciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        encuesta_id INTEGER NOT NULL,
        texto TEXT NOT NULL,
        votos INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (encuesta_id) REFERENCES encuestas(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS votos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        encuesta_id INTEGER NOT NULL,
        opcion_id INTEGER NOT NULL,
        votante TEXT NOT NULL,
        FOREIGN KEY (encuesta_id) REFERENCES encuestas(id)
    )''')

    admin = c.execute("SELECT id FROM usuarios WHERE rol='admin'").fetchone()
    if not admin:
        c.execute("INSERT INTO usuarios (username, password, rol, activo) VALUES (?,?,?,1)",
                  ('admin', generate_password_hash('admin123'), 'admin'))

    conn.commit()
    conn.close()