import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('osint.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            comando TEXT,
            termo TEXT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_consulta(user_id, username, comando, termo):
    conn = sqlite3.connect('osint.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO historico (user_id, username, comando, termo, data)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, comando, termo, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def obter_historico(limit=10):
    conn = sqlite3.connect('osint.db')
    cur = conn.cursor()
    cur.execute('SELECT username, comando, termo, data FROM historico ORDER BY id DESC LIMIT ?', (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
