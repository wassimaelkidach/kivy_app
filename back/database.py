from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv # Import load_dotenv

# --- IMPORTANT: Load environment variables from .env file ---
# This line tells python-dotenv to load variables from the .env file
# located in the same directory as this script (back/.env inside the container).
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# --- Get DB URL components from Environment Variables ---
# These variables are now loaded from back/.env thanks to load_dotenv().
# Use MYSQL_ROOT_PASSWORD for the password as that's what the DB is configured with.
MYSQL_USER = os.getenv("MYSQL_USER") # This will likely be 'root' from your .env
MYSQL_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD") # Use MYSQL_ROOT_PASSWORD for the password
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# --- DEBUG PRINTS: Check individual env vars ---
print(f"DEBUG: MYSQL_USER={MYSQL_USER}")
print(f"DEBUG: MYSQL_PASSWORD={MYSQL_PASSWORD}") # Be cautious with sensitive info in logs
print(f"DEBUG: MYSQL_DATABASE={MYSQL_DATABASE}")
# --- END DEBUG PRINTS ---

# Construct the DATABASE_URL
# Ensure the user is 'root' as per your MySQL container configuration
DATABASE_URL = f"mysql+pymysql://root:{MYSQL_PASSWORD}@db:3306/{MYSQL_DATABASE}?charset=utf8mb4"

# --- DEBUG PRINTS: Print the constructed DATABASE_URL ---
print(f"DEBUG: Constructed DATABASE_URL={DATABASE_URL}")
# --- END DEBUG PRINTS ---

if MYSQL_USER is None or MYSQL_PASSWORD is None or MYSQL_DATABASE is None:
    print("ERROR: One or more MySQL environment variables (MYSQL_USER, MYSQL_ROOT_PASSWORD, MYSQL_DATABASE) are not set!")
    # For production, you might want to raise an exception to prevent startup:
    raise ValueError("Missing MySQL environment variables. Check .env file and container logs.")

# --- Create the SQLAlchemy engine ---
engine = create_engine(DATABASE_URL, echo=True) # echo=True for debugging, set to False for production

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- Import models here ---
from back.models import User, Projet, Dispo, Favori # Ensure all models used are imported

# --- CRITICAL CHANGE: Create database tables if they don't exist ---
# This line will create all tables defined in your models (User, Projet, etc.)
# connected to Base, in the database connected via 'engine'.
# This is usually run once on application startup in development.
Base.metadata.create_all(bind=engine)

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
