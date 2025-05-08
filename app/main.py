from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()
DATA_FILE="notes.txt"


DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

class Nota(BaseModel):
    title: str
    contenido: str

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.get("/")
async def root():
    return {"message": "hola desde raiz"}

@app.get("/notes")
async def get_notes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, contenido FROM notas ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        notas = [{"id": row[0], "title": row[1], "contenido": row[2]} for row in rows]
        return {"notas": notas}
    except Exception as e:
        return {"error": str(e)}

@app.post("/notes")
async def create_note(nota: Nota):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notas (title, contenido) VALUES (%s, %s) RETURNING id",
            (nota.title, nota.contenido)
        )
        nota_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(f"id = {nota_id} | titulo = {nota.title} | contenido = {nota.contenido}\n")

        return {"message": "Nota guardada correctamente", "id": nota_id}
    except Exception as e:
        return {"error": str(e)}
