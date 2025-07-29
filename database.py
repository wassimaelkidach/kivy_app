from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# --- IMPORTANT: Get DB URL from Environment Variable ---
# DigitalOcean App Platform will inject this variable.
# It might be named DATABASE_URL, or DB_URL, or MYSQL_URL,
# depending on how you configure your database connection on DO.
# A common one for DO Managed Databases is DATABASE_URL
DATABASE_URL = os.getenv("MYSQL_URL_DEFAULT") # Or os.getenv("MYSQL_URL") or similar

# --- DEBUG PRINTS ---
print(f"DEBUG: Constructed DATABASE_URL={DATABASE_URL}")
# --- END DEBUG PRINTS ---

if DATABASE_URL is None:
    print("ERROR: DATABASE_URL environment variable is not set!")
    # For production, you might want to raise an exception to prevent startup:
    # raise ValueError("DATABASE_URL environment variable is not set!")
    # Keeping it as a print for now to see the error.

# --- Create the SQLAlchemy engine ---
# For DigitalOcean Managed MySQL, you generally don't need explicit SSL connect_args.
# The platform handles the secure connection.
engine = create_engine(DATABASE_URL, echo=True) # echo=True for debugging, set to False for production

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- Import models here ---
from models import User, Projet, Dispo, Favori # Ensure all models used are imported

# --- Database Helper Functions ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ... (Your existing add_favori, remove_favori, is_favori functions) ...
def add_favori(db: Session, user_id: int, projet_id: int) -> bool:
    # Vérifie s'il existe déjà
    favori_exists = db.query(Favori).filter_by(user_id=user_id, projet_id=projet_id).first()
    if favori_exists:
        return False

    favori = Favori(user_id=user_id, projet_id=projet_id)
    db.add(favori)
    db.commit()
    db.refresh(favori)
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