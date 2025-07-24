from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
from database import SessionLocal
from models import User, Projet, Dispo, Favori
from database import add_favori, remove_favori, is_favori

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#signup
class SignupData(BaseModel):
    name: str
    telephone: str
    email: str
    password: str

@app.post("/signup")
def signup(data: SignupData, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email already used")
        
        hashed_password = pwd_context.hash(data.password)
        user = User(name=data.name, email=data.email, password=hashed_password)
        user.telephone = data.telephone
        db.add(user)
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        print(f"Error during signup: {str(e)}")  # Log l'erreur dans la console
        raise HTTPException(status_code=500, detail=str(e))
    
#login
class LoginData(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "user_id": user.id}

#email check
class EmailCheck(BaseModel):
    email: str

@app.post("/check-email")
def check_email(data: EmailCheck, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == data.email).first() is not None
    return {"exists": exists}

#projets
class ProjectOut(BaseModel):
    id: int
    code_projet: str
    nom_projet: str
    image_base64: str | None

    class Config:
        from_attributes = True

@app.get("/projects", response_model=List[ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Projet).all()
    result = []
    for project in projects:
        image_base64 = None
        if project.images:
            image_base64 = base64.b64encode(project.images).decode('utf-8')
        result.append({
            "id": project.id,
            "code_projet": project.code_projet,
            "nom_projet": project.nom_projet,
            "image_base64": image_base64
        })
    return result

#profile
class ProfileOut(BaseModel):
    name: str
    email: str
    telephone: str

@app.get("/profile/{user_id}", response_model=ProfileOut)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ProfileOut(name=user.name, email=user.email, telephone=user.telephone)

#update profile
class ProfileUpdate(BaseModel):
    user_id: int
    name: str
    telephone: str
    email: str
    password: Optional[str] = None

@app.post("/profile/update")
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = data.name
    user.telephone = data.telephone
    user.email = data.email
    if data.password:
        user.password = pwd_context.hash(data.password)
    db.commit()
    return {"success": True}

#details projets
class DispoOut(BaseModel):
    type_lg: str
    superfide_min: float
    superfide_max: float
    prix: int
    nombre_disponible: int

    class Config:
        from_attributes = True

class ProjectDetailsOut(BaseModel):
    nom_projet: str
    code_projet: str
    dispos: List[DispoOut]

    class Config:
        from_attributes = True

@app.get("/project-details/{project_id}", response_model=ProjectDetailsOut)
def get_project_details(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Projet).filter(Projet.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    dispos = db.query(Dispo).filter(Dispo.code_projet == project.code_projet).all()

    return ProjectDetailsOut(
        nom_projet=project.nom_projet,
        code_projet=project.code_projet,
        dispos=[
            DispoOut(
                type_lg=d.type_lg,
                superfide_min=d.superfide_min,
                superfide_max=d.superfide_max,
                prix=d.prix,
                nombre_disponible=d.nombre_disponible
        ) for d in dispos]
    )

#favoris
class FavoriData(BaseModel):
    user_id: int
    projet_id: int

@app.post("/favorites/add")
def add_favorite(data: FavoriData, db: Session = Depends(get_db)):
    if add_favori(db, data.user_id, data.projet_id):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Already added or error")

@app.post("/favorites/remove")
def remove_favorite(data: FavoriData, db: Session = Depends(get_db)):
    if remove_favori(db, data.user_id, data.projet_id):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Favorite not found or error")

@app.post("/favorites/check")
def is_favorite(data: FavoriData, db: Session = Depends(get_db)):
    return {"is_favorite": is_favori(db, data.user_id, data.projet_id)}

@app.get("/favorites/{user_id}")
def get_favorites(user_id: int, db: Session = Depends(get_db)):
    
    projets = db.query(Projet).join(Favori, Favori.projet_id == Projet.id).filter(Favori.user_id == user_id).all()
    result = []
    for p in projets:
        image_base64 = base64.b64encode(p.images).decode('utf-8') if p.images else None
        result.append({
            "id": p.id,
            "code_projet": p.code_projet,
            "nom_projet": p.nom_projet,
            "image_base64": image_base64
        })
    return result
