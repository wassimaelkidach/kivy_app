import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def create_connection():
    """Connect to MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to MySQL Workbench!")
        return conn
    except Error as e:
        print(f"❌ Connection failed: {e}")
        return None

def initialize_database():
    """Initialise toutes les tables de la base de données"""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            telephone VARCHAR(15),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS projets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code_projet VARCHAR(20) UNIQUE,
            nom_projet VARCHAR(100),
            ville VARCHAR(45),
            localisation VARCHAR(100),
            description TEXT,
            images LONGBLOB
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dispos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code_projet VARCHAR(20),
            type_lg VARCHAR(50),
            superfide_min DECIMAL(10,0),
            superfide_max DECIMAL(10,0),
            prix DECIMAL(12,0),
            nombre_disponible INT,
            FOREIGN KEY (code_projet) REFERENCES projets(code_projet)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS favoris (
            user_id INT NOT NULL,
            projet_id INT NOT NULL,
            PRIMARY KEY (user_id, projet_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (projet_id) REFERENCES projets(id) ON DELETE CASCADE
        )
        """
    ]
    
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            for table_sql in tables:
                cursor.execute(table_sql)
            conn.commit()
            print("✅ Toutes les tables sont initialisées")
        except Error as e:
            print(f"❌ Erreur d'initialisation: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

def check_email_exists(email):
    """Check if email exists in MySQL database"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Error checking email: {e}")
            return True  # Assume exists if error occurs
        finally:
            conn.close()
    return True

def create_user(name, email, password):
    """Create new user in MySQL database"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            conn.commit()
            return cursor.rowcount == 1
        except Error as e:
            print(f"User Creation Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False
    
def validate_login(email, password):
    """Authenticate user credentials"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM users WHERE email = %s AND password = %s",
                (email, password)
            )
            result = cursor.fetchone()
            if result is not None:  # Vérifie explicitement si un résultat existe
                return result[0]  # Retourne l'ID utilisateur
            return None
        except Error as e:
            print(f"Login Validation Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def add_favori(user_id, projet_id):
    conn = create_connection()
    if conn:
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO favoris (user_id, projet_id) VALUES (%s, %s)",
                (user_id, projet_id)
            )
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding favorite: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            conn.close()
    return False

def remove_favori(user_id, projet_id):
    conn = create_connection()
    if conn:
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM favoris WHERE user_id = %s AND projet_id = %s",
                (user_id, projet_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error removing favorite: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            conn.close()
    return False

def is_favori(user_id, projet_id):
    conn = create_connection()
    if conn:
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM favoris WHERE user_id = %s AND projet_id = %s",
                (user_id, projet_id)
            )
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Error checking favorite: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            conn.close()
    return False