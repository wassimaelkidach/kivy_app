from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

USERNAME = os.getenv("MYSQLUSER")
PASSWORD = os.getenv("MYSQLPASSWORD")
HOST = os.getenv("MYSQLHOST")
PORT = os.getenv("MYSQLPORT")
DB_NAME = os.getenv("MYSQLDATABASE")

# --- DEBUG PRINTS ---
print(f"DEBUG: MYSQLUSER={USERNAME}")
print(f"DEBUG: MYSQLPASSWORD={PASSWORD}")
print(f"DEBUG: MYSQLHOST={HOST}")
print(f"DEBUG: MYSQLPORT={PORT}")
print(f"DEBUG: MYSQLDATABASE={DB_NAME}")
# --- END DEBUG PRINTS ---


# --- Construct the DATABASE_URL string ---
# Added checks to ensure variables are not None before formatting
if any(v is None for v in [USERNAME, PASSWORD, HOST, PORT, DB_NAME]):
    print("ERROR: One or more database environment variables are None!")
    # You might want to raise an exception here or handle it more gracefully
    # For now, let it proceed to crash at create_engine to see the full traceback if it does.
    # Optionally, to prevent the "invalid literal for int()" error from malformed URL:
    DATABASE_URL = "invalid_db_url_due_to_none_vars" # This will cause a different error but prevents the int() conversion error
else:
    DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}?charset=utf8mb4"

print(f"DEBUG: Constructed DATABASE_URL={DATABASE_URL}") # Print the constructed URL

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

from sqlalchemy.orm import Session
from models import Favori

def add_favori(db: Session, user_id: int, projet_id: int) -> bool:
    # Vérifie s'il existe déjà
    favori_exists = db.query(Favori).filter_by(user_id=user_id, projet_id=projet_id).first()
    if favori_exists:
        return False

    favori = Favori(user_id=user_id, projet_id=projet_id)
    db.add(favori)
    db.commit()
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