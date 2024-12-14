import uvicorn
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import hashlib

app = FastAPI()
templates = Jinja2Templates(directory="templates")

notes = {}
counter_notes = 0

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
        Обработчик GET-запроса для главной страницы.
        Возвращает HTML-шаблон с запросом.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add_note")
async def add_note(request: Request, secret_phrase: str = Form(...), note_text: str = Form(...)) -> object:
    """
       Обработчик POST-запроса для добавления новой заметки.

       Принимает секретную фразу и текст заметки,
       хеширует секретную фразу и сохраняет заметку.
    """
    global counter_notes
    counter_notes += 1
    hash_object = hashlib.sha256(secret_phrase.encode()).hexdigest()
    notes[counter_notes] = {"secret_phrase": hash_object, "note_text": note_text}
    return templates.TemplateResponse("note.html", {
        "request": request,
        "note_text": note_text,
        "note_id": counter_notes,
        "secret_phrase": hash_object
    })

@app.post("/get_note")
async def get_note(request: Request, note_id: int = Form(...), secret_phrase: str = Form(...)) -> object:
    """
        Обработчик POST-запроса для получения заметки по ID.

        Проверяет, существует ли заметка и соответствует ли
        секретная фраза хешу, если да, возвращает текст заметки.
    """
    note = notes.get(note_id) # Получаем заметку по ID
    # Проверяем, существует ли заметка и соответствует ли секретная фраза
    if note and note["secret_phrase"] == secret_phrase:
        return templates.TemplateResponse("get_note.html", {"request": request, "note_text": note["note_text"]})
    # Если заметка не найдена, возращаем ошибку 404
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

