"""
SecureNotes API  —  Weeks 16-17 Lab (INSTRUCTOR / ANSWER KEY)
Web Systems and Technologies

This is the SAME app you secured in Weeks 13-14 and tested in Week 15.
Nothing about the API changes here. What's new is the front end in
app/static/ and the pipeline in .github/workflows/ — that's where the
Week 16 (accessibility + performance) and Week 17 (CI/CD) work happens.

The only line added to the backend is the static mount at the bottom,
so the API can serve the front-end page at /app.

Run it:
    uvicorn app.main:app --reload
Then open:
    http://127.0.0.1:8000/app/      (the SecureNotes front end)
    http://127.0.0.1:8000/docs      (the API)
"""

import os
import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError

app = FastAPI(title="SecureNotes API (Weeks 16-17)", version="3.0")

# --- config ---------------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")   # real deploy: set this
ALGORITHM = "HS256"
TOKEN_MINUTES = 30

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# --- password hashing (bcrypt) --------------------------------------------
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(raw: str) -> str:
    return pwd.hash(raw)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd.verify(raw, hashed)

# --- JSON Web Tokens ------------------------------------------------------
def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    claims = {"sub": username, "exp": expire}
    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)

def read_token(token: str):
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return claims.get("sub")
    except JWTError:
        return None

# --- database (in-memory SQLite, seeded on startup) -----------------------
db = sqlite3.connect(":memory:", check_same_thread=False)
db.row_factory = sqlite3.Row

def init_db():
    db.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL
        );
        """
    )
    db.execute("INSERT INTO users (username,password,is_admin) VALUES (?,?,1)", ("admin", hash_password("admin123")))
    db.execute("INSERT INTO users (username,password,is_admin) VALUES (?,?,0)", ("alice", hash_password("alicepass")))
    db.execute("INSERT INTO users (username,password,is_admin) VALUES (?,?,0)", ("bob", hash_password("bobpass")))
    db.execute("INSERT INTO notes (owner_id,title,body) VALUES (2,'Alice diary','Alice secret note')")
    db.execute("INSERT INTO notes (owner_id,title,body) VALUES (3,'Bob plans','Bob secret note')")
    db.commit()

def reset_database():
    db.execute("DROP TABLE IF EXISTS users")
    db.execute("DROP TABLE IF EXISTS notes")
    init_db()

init_db()

# --- models ---------------------------------------------------------------
class Credentials(BaseModel):
    username: str
    password: str

class NewNote(BaseModel):
    title: str
    body: str

# --- the auth dependency (fails closed) -----------------------------------
def get_current_user(token: str = Depends(oauth2)):
    username = read_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return row

def require_admin(user=Depends(get_current_user)):
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admins only")
    return user

# --- routes ---------------------------------------------------------------
@app.post("/register")
def register(creds: Credentials):
    existing = db.execute("SELECT id FROM users WHERE username = ?", (creds.username,)).fetchone()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")
    db.execute(
        "INSERT INTO users (username,password,is_admin) VALUES (?,?,0)",
        (creds.username, hash_password(creds.password)),
    )
    db.commit()
    return {"message": f"user {creds.username} created"}

@app.post("/login")
def login(creds: Credentials):
    row = db.execute(
        "SELECT id, username, password FROM users WHERE username = ?", (creds.username,)
    ).fetchone()
    if row is None or not verify_password(creds.password, row["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": create_token(row["username"]), "token_type": "bearer"}

@app.get("/notes")
def list_my_notes(user=Depends(get_current_user)):
    rows = db.execute("SELECT * FROM notes WHERE owner_id = ?", (user["id"],)).fetchall()
    return [dict(r) for r in rows]

@app.get("/notes/{note_id}")
def get_note(note_id: int, user=Depends(get_current_user)):
    row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if row["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your note")
    return dict(row)

@app.post("/notes")
def create_note(note: NewNote, user=Depends(get_current_user)):
    cur = db.execute(
        "INSERT INTO notes (owner_id,title,body) VALUES (?,?,?)",
        (user["id"], note.title, note.body),
    )
    db.commit()
    return {"id": cur.lastrowid, "title": note.title}

@app.get("/admin/users")
def list_all_users(admin=Depends(require_admin)):
    rows = db.execute("SELECT id, username, is_admin FROM users").fetchall()
    return [dict(r) for r in rows]

@app.get("/")
def home():
    return {"service": "SecureNotes API", "docs": "/docs", "frontend": "/app/"}

# --- the front end --------------------------------------------------------
# Serves app/static/ at /app  (index.html is the SecureNotes page you harden
# in Part A). The accessibility & performance tests read those files directly.
_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/app", StaticFiles(directory=_static_dir, html=True), name="frontend")
