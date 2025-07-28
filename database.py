from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session # Import Session here
import os

# Use the combined URL variable if available and preferred
# DATABASE_URL = os.getenv("MYSQL_PUBLIC_URL") 
DATABASE_URL = "mysql+pymysql://root:vKUZUWxcTiuGmUzjrgHyKdoDMaWxPFFb@metro.proxy.rlwy.net:25998/railway"

# --- DEBUG PRINTS ---
print(f"DEBUG: Using combined DATABASE_URL={DATABASE_URL}")
# --- END DEBUG PRINTS ---

if DATABASE_URL is None:
    print("ERROR: Combined DATABASE_URL is None! Database connection will fail.")

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- Import models here (or at the top if no circular dependency) ---
# It's usually better to import models at the top level to avoid
# potential circular imports if models also import from db.py
# If 'Favori' is defined in models.py, make sure models.py doesn't try
# to import SessionLocal or engine in a way that causes a circular import.
from .models import Favori # Assuming models.py is in the same directory


# --- Database Helper Functions ---

def get_db():
    """Dependency for FastAPI to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_favori(db: Session, user_id: int, projet_id: int) -> bool:
    # Vérifie s'il existe déjà
    favori_exists = db.query(Favori).filter_by(user_id=user_id, projet_id=projet_id).first()
    if favori_exists:
        return False

    favori = Favori(user_id=user_id, projet_id=projet_id)
    db.add(favori)
    db.commit()
    db.refresh(favori) # Refresh to get any default values (e.g., auto-incremented ID)
    return True

def remove_favori(db: Session, user_id: int, projet_id: int) -> bool:
    favori = db.query(Favori).filter_by(user_id=user_id, projet_id=projet_id).first()
    if favori:
        db.delete(favori)
        db.commit()
        return True
    return False

def is_favori(db: Session, user_id: int, projet_id: int) -> bool:
    return db.query(Favori).filter_by(user_id=user_id, projet_id=projet_id).first() is not None
