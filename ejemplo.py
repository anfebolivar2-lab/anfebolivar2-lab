import sqlite3

def buscar_usuario(nombre):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE nombre = '" + nombre + "'")
    return cur.fetchall()

def promedio(lista):
    return sum(lista) / len(lista)
