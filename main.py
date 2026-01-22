# MVP Backend - Gestión de Producción Editorial
# Stack: Python + FastAPI + SQLite (dev)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime

# =========================
# APP (SOLO UNA VEZ)
# =========================
app = FastAPI(title="Gestión de Producción")

# =========================
# VISTAS HTML (INTERFAZ)
# =========================

@app.get("/", response_class=HTMLResponse)
def home():
    return open("index.html", encoding="utf-8").read()

@app.get("/roles", response_class=HTMLResponse)
def roles():
    return open("roles.html", encoding="utf-8").read()

@app.get("/jefe1", response_class=HTMLResponse)
def jefe1():
    return open("jefe1.html", encoding="utf-8").read()

@app.get("/jefe2", response_class=HTMLResponse)
def jefe2():
    return open("jefe2.html", encoding="utf-8").read()

@app.get("/admin", response_class=HTMLResponse)
def admin():
    return open("admin.html", encoding="utf-8").read()

# =========================
# AUTH (TEMPORAL / MOCK)
# =========================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# =========================
# MODELOS
# =========================

class User(BaseModel):
    id: int
    name: str
    role: str  # admin, jefe, gif, editorial

class Folder(BaseModel):
    id: int
    name: str
    state: str
    owner_team: str  # gif o editorial
    state_started_at: datetime

class File(BaseModel):
    id: int
    folder_id: int
    name: str
    state: str
    assigned_to: str
    state_started_at: datetime

# =========================
# DATA MOCK (TEMPORAL)
# =========================

users = [
    User(id=1, name="Admin", role="admin"),
    User(id=2, name="Nath", role="jefe"),
    User(id=3, name="Jacobo", role="jefe"),
]

now = datetime.now()

folders = [
    Folder(
        id=1,
        name="Unidad Álgebra 6°",
        state="EN_EDITORIAL",
        owner_team="gif",
        state_started_at=now.replace(hour=9)
    ),
    Folder(
        id=2,
        name="Guía Trigonometría 10°",
        state="EN_CONTROL_CALIDAD",
        owner_team="editorial",
        state_started_at=now.replace(hour=11)
    ),
]

files = [
    File(
        id=1,
        folder_id=1,
        name="Documento 1 - Introducción",
        state="EN_PRODUCCION",
        assigned_to="Diseñador A",
        state_started_at=now.replace(hour=10)
    ),
    File(
        id=2,
        folder_id=1,
        name="Documento 2 - Ejercicios",
        state="ASIGNADO",
        assigned_to="Diseñador B",
        state_started_at=now.replace(hour=9, minute=30)
    ),
    File(
        id=3,
        folder_id=2,
        name="Documento Final",
        state="EN_CORRECCION",
        assigned_to="Editor C",
        state_started_at=now.replace(hour=12)
    ),
]


# =========================
# DEPENDENCIAS
# =========================

def get_current_user(token: str = Depends(oauth2_scheme)):
    # TEMPORAL: siempre admin
    return users[0]

# =========================
# ENDPOINTS API
# =========================

@app.get("/folders", response_model=List[Folder])
def list_folders(user: User = Depends(get_current_user)):
    return folders

@app.post("/folders", response_model=Folder)
def create_folder(folder: Folder, user: User = Depends(get_current_user)):
    if user.role not in ["admin", "jefe"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    folders.append(folder)
    return folder

@app.get("/files/{folder_id}", response_model=List[File])
def list_files(folder_id: int, user: User = Depends(get_current_user)):
    return [f for f in files if f.folder_id == folder_id]

@app.post("/files", response_model=File)
def create_file(file: File, user: User = Depends(get_current_user)):
    if user.role not in ["admin", "jefe"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    files.append(file)
    return file

def hours_in_state(start_time: datetime) -> float:
    delta = datetime.now() - start_time
    return round(delta.total_seconds() / 3600, 2)


@app.get("/jefe/{team}")
def view_team(team: str):
    team_folders = []
    for f in folders:
        if f.owner_team == team:
            team_folders.append({
                "id": f.id,
                "name": f.name,
                "state": f.state,
                "hours_in_state": hours_in_state(f.state_started_at)
            })

    team_files = []
    for fi in files:
        if any(fi.folder_id == fo.id for fo in folders if fo.owner_team == team):
            team_files.append({
                "id": fi.id,
                "name": fi.name,
                "state": fi.state,
                "assigned_to": fi.assigned_to,
                "hours_in_state": hours_in_state(fi.state_started_at)
            })

    return {
        "team": team,
        "folders": team_folders,
        "files": team_files
    }
