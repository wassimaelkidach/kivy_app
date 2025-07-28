from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session # Import Session here
import os

# --- Database Credentials from Environment Variables ---
USERNAME = os.getenv("MYSQLUSER")
PASSWORD = os.getenv("MYSQLPASSWORD")
HOST = os.getenv("MYSQLHOST")
PORT = os.getenv("MYSQLPORT")
DB_NAME = os.getenv("MYSQLDATABASE")

# --- Define the path to your DigitalOcean CA certificate ---
# You MUST download this file from your DigitalOcean database cluster
# and place it in the root of your GitHub repository.
# Railway will copy it to /app/ when deploying your service.
SSL_CA_PATH = "/app/do-ca-certificate.crt" # Make sure this file exists in your repo root

# --- Construct the DATABASE_URL string ---
# Using f-string for readability and directly embedding variables
DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}?charset=utf8mb4"

# --- Connection arguments for SQLAlchemy, including SSL ---
# This dictionary will be passed to create_engine
connect_args = {
    "ssl": {
        "ca": SSL_CA_PATH
        # PyMySQL often handles 'REQUIRED' mode if 'ca' is provided.
        # If you encounter specific SSL negotiation errors, you might need
        # to add 'ssl_mode': 'REQUIRED' or 'ssl_verify_cert': True,
        # but try with just 'ca' first.
    }
}

# --- Create the SQLAlchemy engine ---
# Set echo=False for production to avoid verbose logging
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

# --- Create SessionLocal and Base ---
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
