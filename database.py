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
    """Create tables if missing"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
                    password VARCHAR(100)
                )
            """)
            conn.commit()
        except Error as e:
            print(f"Error creating tables: {e}")
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
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Login Validation Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False
