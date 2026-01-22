# MVP Backend - Gestión de Producción Editorial
# Stack: Python + FastAPI + SQLite (dev)

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Gestión de Producción")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- MODELOS ---
class User(BaseModel):
    id: int
    name: str
    role: str  # admin, jefe, gif, editorial

class Folder(BaseModel):
    id: int
    name: str
    state: str  # CREADA_GIF, EN_EDITORIAL, EN_CONTROL_CALIDAD, EN_CORRECCIONES, FINALIZADA

class File(BaseModel):
    id: int
    folder_id: int
    name: str
    state: str  # ASIGNADO, EN_PRODUCCION, TERMINADO_EDITORIAL, EN_CORRECCION, APROBADO_FINAL
    assigned_to: int

# --- DATA MOCK (TEMPORAL) ---
users = [
    User(id=1, name="Admin", role="admin"),
    User(id=2, name="Nath", role="jefe"),
    User(id=3, name="Jacobo", role="jefe"),
]

folders = []
files = []

# --- DEPENDENCIAS ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    # TEMPORAL: siempre admin
    return users[0]

# --- ENDPOINTS ---
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
